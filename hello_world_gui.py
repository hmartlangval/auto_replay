import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import threading
import platform
from dotenv import load_dotenv
from utils.code_generator import (
    generate_file_header, generate_imports, generate_screen_detection_function,
    generate_validation_function, generate_replay_function, generate_main_section
)
from utils.file_utils import generate_unique_filename, generate_suggested_name, ensure_sequences_directory
from utils.image_scanner import scan_image_with_bbox, create_advanced_scan_dialog
from utils.windows_automation import ManualAutomationHelper

load_dotenv()

# Configuration - Change this to target different applications
APP_TITLE = os.getenv("APP_TITLE")

# Global variables
automation_helper = None

try:
    from pynput import mouse, keyboard
    from pynput.keyboard import Key, Listener as KeyboardListener
    from pynput.mouse import Listener as MouseListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import win32gui, win32api, win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False

# Windows-specific imports for DPI detection
if platform.system() == 'Windows':
    try:
        import ctypes
        from ctypes import wintypes
        WINDOWS_DPI_AVAILABLE = True
    except ImportError:
        WINDOWS_DPI_AVAILABLE = False
else:
    WINDOWS_DPI_AVAILABLE = False

class SequenceRecorder:
    def __init__(self):
        self.recording = False
        self.actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.pressed_keys = set()  # Track currently pressed keys
        self.modifier_keys = {Key.ctrl_l, Key.ctrl_r, Key.alt_l, Key.alt_r, Key.shift, Key.shift_l, Key.shift_r, Key.cmd, Key.cmd_l, Key.cmd_r}
        self.screen_info = None  # Store screen resolution and DPI info
        
        # Text typing detection
        self.typing_buffer = ""  # Buffer to collect typed text
        self.typing_start_time = None  # When typing sequence started
        self.last_key_time = None  # Time of last keystroke
        self.typing_threshold = 0.5  # Max seconds between keystrokes to consider as typing
        
    def get_screen_info(self):
        """Get current screen resolution and DPI information"""
        screen_info = {}
        
        # Get screen resolution using tkinter
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()  # Hide the window
            screen_info['width'] = temp_root.winfo_screenwidth()
            screen_info['height'] = temp_root.winfo_screenheight()
            temp_root.destroy()
        except:
            screen_info['width'] = 1920  # Fallback
            screen_info['height'] = 1080
        
        # Get DPI information
        if WINDOWS_DPI_AVAILABLE:
            try:
                # Get DPI for the primary monitor
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                dpi_x = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
                dpi_y = ctypes.windll.gdi32.GetDeviceCaps(dc, 90)  # LOGPIXELSY
                user32.ReleaseDC(0, dc)
                screen_info['dpi_x'] = dpi_x
                screen_info['dpi_y'] = dpi_y
                screen_info['dpi_scale'] = dpi_x / 96.0  # 96 DPI is 100% scaling
            except:
                screen_info['dpi_x'] = 96
                screen_info['dpi_y'] = 96
                screen_info['dpi_scale'] = 1.0
        else:
            # Fallback for non-Windows or when DPI detection is not available
            screen_info['dpi_x'] = 96
            screen_info['dpi_y'] = 96
            screen_info['dpi_scale'] = 1.0
        
        screen_info['platform'] = platform.system()
        return screen_info
    
    def flush_typing_buffer(self):
        """Flush the typing buffer as a single text action"""
        if self.typing_buffer and self.typing_start_time is not None:
            action = {
                'type': 'type_text',
                'text': self.typing_buffer,
                'time': round(self.typing_start_time - self.start_time, 2)
            }
            self.actions.append(action)
            
        # Reset typing state
        self.typing_buffer = ""
        self.typing_start_time = None
        self.last_key_time = None
    
    def start_recording(self):
        """Start recording mouse and keyboard actions"""
        self.recording = True
        self.actions = []
        self.start_time = time.time()
        
        # Capture current screen information
        self.screen_info = self.get_screen_info()
        
        # Start mouse listener
        self.mouse_listener = MouseListener(
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()
        
    def stop_recording(self):
        """Stop recording actions"""
        self.recording = False
        self.flush_typing_buffer()  # Flush any remaining text
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.recording:
            return
            
        if pressed:  # Only record on press, not release
            # Mouse click interrupts typing sequence
            self.flush_typing_buffer()
            
            current_time = time.time()
            time_interval = round(current_time - self.start_time, 2)
            
            button_name = str(button).split('.')[-1]  # Extract button name
            action = {
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': button_name,
                'time': time_interval
            }
            self.actions.append(action)
            
    def on_key_press(self, key):
        """Handle keyboard press events"""
        if not self.recording:
            return
            
        # Check for ESC key to stop recording
        if key == Key.esc:
            self.flush_typing_buffer()  # Flush any pending text
            self.stop_recording()
            return False  # Stop listener
        
        # Add key to pressed keys set
        self.pressed_keys.add(key)
        
        # Only record action for non-modifier keys
        if key not in self.modifier_keys:
            current_time = time.time()
            time_interval = round(current_time - self.start_time, 2)
            
            # Check for active modifiers
            active_modifiers = []
            if any(mod in self.pressed_keys for mod in [Key.ctrl_l, Key.ctrl_r]):
                active_modifiers.append('ctrl')
            if any(mod in self.pressed_keys for mod in [Key.alt_l, Key.alt_r]):
                active_modifiers.append('alt')
            if any(mod in self.pressed_keys for mod in [Key.shift, Key.shift_l, Key.shift_r]):
                active_modifiers.append('shift')
            if any(mod in self.pressed_keys for mod in [Key.cmd, Key.cmd_l, Key.cmd_r]):
                active_modifiers.append('cmd')
            
            # Check if this is a regular character that can be typed (no modifiers except shift)
            is_typeable_char = False
            try:
                char = key.char
                if char and char.isprintable() and not active_modifiers:
                    is_typeable_char = True
                elif char and char.isprintable() and active_modifiers == ['shift']:
                    # Shift+character is still just typing (uppercase/symbols)
                    is_typeable_char = True
            except AttributeError:
                # Not a character key
                pass
            
            if is_typeable_char:
                # This is a typeable character - add to typing buffer
                try:
                    char = key.char
                    
                    # Check if we should start a new typing sequence or continue existing one
                    if (self.last_key_time is None or 
                        current_time - self.last_key_time > self.typing_threshold):
                        # Start new typing sequence
                        self.flush_typing_buffer()  # Flush any previous buffer
                        self.typing_buffer = char
                        self.typing_start_time = current_time
                    else:
                        # Continue existing typing sequence
                        self.typing_buffer += char
                    
                    self.last_key_time = current_time
                    
                except AttributeError:
                    # Shouldn't happen since we checked for char above, but just in case
                    pass
            else:
                # This is a special key or key combination - flush typing buffer and record as separate action
                self.flush_typing_buffer()
                
                # Format key name with modifiers
                key_name = self.format_key_combination(key, active_modifiers)
                
                action = {
                    'type': 'key_press',
                    'key': key_name,
                    'modifiers': active_modifiers,
                    'time': time_interval
                }
                self.actions.append(action)
    
    def on_key_release(self, key):
        """Handle keyboard release events"""
        if not self.recording:
            return
        
        # Remove key from pressed keys set
        self.pressed_keys.discard(key)
        
    def format_key_combination(self, key, modifiers):
        """Format key combination with modifiers"""
        try:
            # Regular character keys
            base_key = key.char
        except AttributeError:
            # Special keys
            key_str = str(key).split('.')[-1]
            special_keys = {
                'enter': 'enter',
                'space': 'space',
                'tab': 'tab',
                'backspace': 'backspace',
                'delete': 'delete',
                'up': 'up',
                'down': 'down',
                'left': 'left',
                'right': 'right',
                'home': 'home',
                'end': 'end',
                'page_up': 'page_up',
                'page_down': 'page_down',
                'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
                'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
                'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
            }
            base_key = special_keys.get(key_str.lower(), key_str.lower())
        
        # Build combination string
        if modifiers:
            combo_parts = []
            if 'ctrl' in modifiers:
                combo_parts.append('ctrl')
            if 'alt' in modifiers:
                combo_parts.append('alt')
            if 'shift' in modifiers:
                combo_parts.append('shift')
            if 'cmd' in modifiers:
                combo_parts.append('cmd')
            combo_parts.append(base_key)
            return '+'.join(combo_parts)
        else:
            return base_key
    
    def format_key_name(self, key):
        """Format key name with curly brackets for special keys (legacy method)"""
        try:
            # Regular character keys
            return key.char
        except AttributeError:
            # Special keys
            key_str = str(key).split('.')[-1]
            special_keys = {
                'enter': '{Enter}',
                'space': '{Space}',
                'tab': '{Tab}',
                'shift': '{Shift}',
                'ctrl': '{Ctrl}',
                'alt': '{Alt}',
                'cmd': '{Cmd}',
                'backspace': '{Backspace}',
                'delete': '{Delete}',
                'up': '{Up}',
                'down': '{Down}',
                'left': '{Left}',
                'right': '{Right}',
                'home': '{Home}',
                'end': '{End}',
                'page_up': '{PageUp}',
                'page_down': '{PageDown}',
                'f1': '{F1}', 'f2': '{F2}', 'f3': '{F3}', 'f4': '{F4}',
                'f5': '{F5}', 'f6': '{F6}', 'f7': '{F7}', 'f8': '{F8}',
                'f9': '{F9}', 'f10': '{F10}', 'f11': '{F11}', 'f12': '{F12}'
            }
            return special_keys.get(key_str.lower(), f'{{{key_str}}}')
    
    def save_sequence(self, sequence_name):
        """Save the recorded sequence as a Python file using utilities"""
        if not self.actions:
            return False, "No actions recorded"
            
        # Use utility functions for file operations
        sequences_dir = ensure_sequences_directory()
        filename, clean_sequence_name = generate_unique_filename(sequence_name, sequences_dir)
        
        try:
            with open(filename, 'w') as f:
                # Generate all sections using utility functions
                f.write(generate_file_header(clean_sequence_name, self.screen_info))
                f.write(generate_imports(self.screen_info))
                f.write(generate_screen_detection_function(self.screen_info))
                f.write(generate_validation_function(self.screen_info))
                f.write(generate_replay_function(clean_sequence_name, self.actions, self.screen_info))
                f.write(generate_main_section(clean_sequence_name))
        except Exception as e:
            return False, f"Failed to write file: {str(e)}"
        
        return True, f"Sequence saved as: {filename}"

def initialize_automation_helper():
    """Initialize the automation helper to target this application"""
    global automation_helper
    
    if not PYWIN32_AVAILABLE:
        print("❌ pywin32 not available - Windows automation disabled")
        _update_status_label("Windows automation disabled (missing pywin32)")
        return
    
    try:
        # Small delay to ensure window is fully created
        root.after(1000, lambda: _setup_automation_helper())
    except Exception as e:
        print(f"Error initializing automation helper: {e}")
        automation_helper = None

def _setup_automation_helper():
    """Helper function to set up automation after window is ready"""
    global automation_helper
    try:
        automation_helper = ManualAutomationHelper(target_window_title=APP_TITLE)
        print(f"✅ Automation helper initialized for: '{APP_TITLE}'")
        automation_helper.setup_window(bbox = (56, 37, 100, 609))
        
        # Verify the automation helper is working
        if automation_helper.is_window_valid():
            window_info = automation_helper.get_window_info()
            print(f"Window info: {window_info}")
            
            # Update status label to show success
            _update_status_label("Windows automation ready ✅")
        else:
            print("⚠️ Warning: Window handle is not valid")
            _update_status_label("Windows automation warning ⚠️")
            
    except Exception as e:
        print(f"❌ Error setting up automation helper: {e}")
        automation_helper = None
        _update_status_label("Windows automation failed ❌")

def _update_status_label(automation_status):
    """Update the status label with new automation status"""
    try:
        pynput_status = "Ready to record sequences" if PYNPUT_AVAILABLE else "Install pynput to enable recording"
        status_text = f"{pynput_status} | {automation_status}"
        
        # Find the status label and update it
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label) and "sequences" in widget.cget("text"):
                widget.config(text=status_text)
                break
    except Exception as e:
        print(f"Error updating status label: {e}")

def scan_image():
    """Scan for plus-collapsed.png image within the automation helper's bounding box"""
    global automation_helper
    
    if not PYWIN32_AVAILABLE:
        messagebox.showerror("Error", "pywin32 is required for Windows automation.\n\nPlease install it using:\npip install pywin32")
        return
    
    if not automation_helper:
        messagebox.showerror("Error", "Automation helper is not initialized.\n\nPlease wait for initialization or restart the application.")
        return
    
    # Use the utility function from image_scanner
    result = scan_image_with_bbox(automation_helper, "plus-collapsed.png", threshold=0.8)
    
    if result['success']:
        if result['found_count'] > 0:
            # Format the results message
            message = f"Found {result['found_count']} instance(s) of '{result['image_name']}':\n"
            message += f"Search area: {result['search_area']}\n"
            message += f"Window bbox: {result['bbox']}\n\n"
            
            for i, location in enumerate(result['locations'], 1):
                abs_pos = location['absolute']
                rel_pos = location['relative']
                message += f"{i}. Absolute: ({abs_pos[0]}, {abs_pos[1]}) | Relative: ({rel_pos[0]}, {rel_pos[1]})\n"
            
            messagebox.showinfo("Image Scan Results", message)
        else:
            message = f"No instances of '{result['image_name']}' found in window.\n\n"
            message += f"Search area: {result['search_area']}\n"
            message += f"Window bbox: {result['bbox']}"
            messagebox.showinfo("Image Scan Results", message)
    else:
        messagebox.showerror("Error", result['error'])

def scan_image_advanced():
    """Open advanced image scanning dialog"""
    global automation_helper
    
    if not PYWIN32_AVAILABLE or not automation_helper:
        messagebox.showerror("Error", "Windows automation is not available.")
        return
    
    # Use the utility function from image_scanner
    create_advanced_scan_dialog(root, automation_helper)

def test_automation():
    """Test the automation helper functionality"""
    global automation_helper
    
    if not PYWIN32_AVAILABLE:
        messagebox.showerror("Error", "pywin32 is required for Windows automation.\n\nPlease install it using:\npip install pywin32")
        return
    
    if not automation_helper:
        messagebox.showerror("Error", "Automation helper is not initialized.\n\nPlease wait for initialization or restart the application.")
        return
    
    try:
        # Test window information
        if automation_helper.is_window_valid():
            window_info = automation_helper.get_window_info()
            
            message = f"✅ Automation Helper Test Results:\n\n"
            message += f"Window Title: {window_info.get('title', 'Unknown')}\n"
            message += f"Window Handle: {window_info.get('handle', 'Unknown')}\n"
            message += f"Position: ({window_info.get('left', 0)}, {window_info.get('top', 0)})\n"
            message += f"Size: {window_info.get('width', 0)}x{window_info.get('height', 0)}\n"
            message += f"Visible: {window_info.get('is_visible', False)}\n"
            message += f"Minimized: {window_info.get('is_minimized', False)}\n"
            message += f"Maximized: {window_info.get('is_maximized', False)}\n\n"
            message += "Automation helper is ready for use!"
            
            messagebox.showinfo("Automation Test", message)
        else:
            messagebox.showerror("Error", "Window handle is no longer valid.\n\nThe automation helper may need to be reinitialized.")
    
    except Exception as e:
        messagebox.showerror("Error", f"Error testing automation helper:\n\n{str(e)}")

def record_sequence():
    """Handle the Record Sequence button click"""
    if not PYNPUT_AVAILABLE:
        messagebox.showerror(
            "Missing Dependency", 
            "The pynput library is required for recording sequences.\n\n"
            "Please install it using:\npip install pynput"
        )
        return
    
    # Confirm to proceed
    confirm = messagebox.askyesno(
        "Record Sequence",
        "This will start recording your mouse clicks and keyboard inputs.\n\n"
        "• Mouse clicks will be captured with coordinates\n"
        "• Keyboard inputs will be captured\n"
        "• Press ESC to stop recording\n\n"
        "Do you want to proceed?"
    )
    
    if not confirm:
        return
    
    # Start recording
    global recorder
    recorder = SequenceRecorder()
    
    messagebox.showinfo(
        "Recording Started",
        "Recording has started!\n\n"
        "• Perform your actions now\n"
        "• Press ESC to stop recording\n"
        "• The window will minimize to avoid interference"
    )
    
    # Store current window geometry before minimizing
    global window_geometry
    window_geometry = root.geometry()
    
    # Minimize the main window
    root.iconify()
    
    # Start recording in a separate thread
    def start_recording_thread():
        recorder.start_recording()
        
        # Wait for recording to stop (when ESC is pressed)
        while recorder.recording:
            time.sleep(0.1)
        
        # Recording stopped, restore window and ask for name
        root.after(0, finish_recording)
    
    threading.Thread(target=start_recording_thread, daemon=True).start()

def get_suggested_sequence_name():
    """Get a unique suggested name for the sequence using utility"""
    return generate_suggested_name()

def finish_recording():
    """Finish recording and save sequence"""
    # Restore the main window with original geometry
    root.deiconify()
    root.geometry(window_geometry)  # Restore original size and position
    root.lift()
    
    if not recorder.actions:
        messagebox.showinfo("No Actions", "No actions were recorded.")
        return
    
    # Generate a unique suggested name
    suggested_name = get_suggested_sequence_name()
    
    # Ask for sequence name
    sequence_name = simpledialog.askstring(
        "Save Sequence",
        f"Recording completed! {len(recorder.actions)} actions captured.\n\n"
        "Enter a name for this sequence:",
        initialvalue=suggested_name
    )
    
    if sequence_name:
        success, message = recorder.save_sequence(sequence_name)
        
        if success:
            messagebox.showinfo(
                "Sequence Saved",
                f"Sequence saved successfully!\n\n"
                f"{message}\n"
                f"Actions recorded: {len(recorder.actions)}\n\n"
                "You can now import and run this sequence from anywhere."
            )
        else:
            messagebox.showerror("Error", f"Failed to save the sequence.\n\n{message}")

def main():
    global root
    # Create the main window
    root = tk.Tk()
    root.title("Fiserv Automation")
    root.geometry("500x400")  # Made slightly larger
    root.resizable(True, True)
    
    # Initialize automation helper after window is created
    initialize_automation_helper()
    
    # Create and pack a label
    hello_label = tk.Label(
        root, 
        text="Hello, World!", 
        font=("Arial", 24, "bold"),
        fg="blue",
        pady=20
    )
    hello_label.pack()
    
    # Create a welcome message
    welcome_label = tk.Label(
        root,
        text="Welcome to your first Python GUI application!",
        font=("Arial", 12),
        pady=10
    )
    welcome_label.pack()
    
    # Create buttons frame for scan options
    scan_frame = tk.Frame(root)
    scan_frame.pack(pady=10)
    
    # Create the scan image button (simple)
    scan_button = tk.Button(
        scan_frame,
        text="Scan Image",
        command=scan_image,
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
        padx=15,
        pady=8
    )
    scan_button.pack(side=tk.LEFT, padx=5)
    
    # Create the advanced scan button
    advanced_scan_button = tk.Button(
        scan_frame,
        text="Advanced Scan",
        command=scan_image_advanced,
        font=("Arial", 12),
        bg="#9C27B0",
        fg="white",
        padx=15,
        pady=8
    )
    advanced_scan_button.pack(side=tk.LEFT, padx=5)
    
    # Create the Record Sequence button
    record_button = tk.Button(
        root,
        text="Record Sequence",
        command=record_sequence,
        font=("Arial", 14),
        bg="#FF9800",
        fg="white",
        padx=20,
        pady=10
    )
    record_button.pack(pady=10)
    
    # Create the Test Automation button
    test_automation_button = tk.Button(
        root,
        text="Test Automation",
        command=test_automation,
        font=("Arial", 14),
        bg="#2196F3",
        fg="white",
        padx=20,
        pady=10
    )
    test_automation_button.pack(pady=10)
    
    # Add status label
    pynput_status = "Ready to record sequences" if PYNPUT_AVAILABLE else "Install pynput to enable recording"
    
    if PYWIN32_AVAILABLE:
        automation_status = "Windows automation will initialize shortly..."
    else:
        automation_status = "Install pywin32 for Windows automation"
    
    status_text = f"{pynput_status} | {automation_status}"
    
    status_label = tk.Label(
        root,
        text=status_text,
        font=("Arial", 10),
        fg="green" if PYNPUT_AVAILABLE else "red"
    )
    status_label.pack(pady=5)
    
    # Create an exit button
    exit_button = tk.Button(
        root,
        text="Exit",
        command=root.quit,
        font=("Arial", 12),
        bg="#f44336",
        fg="white",
        padx=20,
        pady=5
    )
    exit_button.pack(pady=10)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 