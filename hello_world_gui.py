import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import threading
import platform
import signal
import sys
import subprocess
from dotenv import load_dotenv
from utils.code_generator import (
    generate_file_header, generate_imports, generate_screen_detection_function,
    generate_validation_function, generate_replay_function, generate_main_section
)
from utils.common import show_modal_input_dialog, show_result_dialog
from utils.file_utils import generate_unique_filename, generate_suggested_name, ensure_sequences_directory
from utils.image_scanner import scan_image_with_bbox, create_advanced_scan_dialog
from utils.windows_automation import ManualAutomationHelper

load_dotenv()

# Configuration loaded from environment (if needed for future extensions)
# APP_TITLE = os.getenv("APP_TITLE")  # Currently unused

# Global variables
root = None
shutdown_in_progress = False
spawned_processes = []  # Track all spawned subprocess processes
btt_process = None  # Track BTT process specifically
btt_button = None  # Reference to BTT button for state changes

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

def scan_image():
    """Scan for plus-collapsed.png image on full screen"""
    if not PYWIN32_AVAILABLE:
        messagebox.showerror("Error", "pywin32 is required for Windows automation.\n\nPlease install it using:\npip install pywin32")
        return
    
    try:
        # Use full screen scanning
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        bounding_box = (0, 0, screen_width, screen_height)
        
        from utils.image_scanner import scan_for_all_occurrences
        locations = scan_for_all_occurrences("plus-collapsed.png", bounding_box, threshold=0.8)
        
        if locations:
            message = f"Found {len(locations)} instance(s) of 'plus-collapsed.png':\n"
            message += f"Search area: {screen_width}x{screen_height} pixels (full screen)\n\n"
            
            for i, (x, y) in enumerate(locations, 1):
                message += f"{i}. Position: ({x}, {y})\n"
            
            messagebox.showinfo("Image Scan Results", message)
        else:
            message = "No instances of 'plus-collapsed.png' found on screen.\n\n"
            message += f"Search area: {screen_width}x{screen_height} pixels (full screen)"
            messagebox.showinfo("Image Scan Results", message)
            
    except Exception as e:
        messagebox.showerror("Error", f"Error during image scan:\n\n{str(e)}")

def scan_image_advanced():
    """Open advanced image scanning dialog"""
    if not PYWIN32_AVAILABLE:
        messagebox.showerror("Error", "pywin32 is required for Windows automation.\n\nPlease install it using:\npip install pywin32")
        return
    
    # Use the utility function from image_scanner with None automation helper (will use full screen)
    create_advanced_scan_dialog(root, None)

def search_window():
    """Search for windows by title using modal input dialog"""
    if not PYWIN32_AVAILABLE:
        messagebox.showerror("Error", "pywin32 is required for Windows automation.\n\nPlease install it using:\npip install pywin32")
        return
    
    # Get search term from user using modal dialog
    search_term = show_modal_input_dialog(
        root,
        title="Search Windows",
        prompt="Enter window title to search for:\n(Will find windows that START WITH this text)",
        initial_value=""
    )
    
    if not search_term:
        return  # User cancelled
    
    try:
        # Import the search function from windows_automation
        from utils.windows_automation import find_windows_by_title_starts_with
        
        # Search for windows
        matching_windows = find_windows_by_title_starts_with(search_term)
        
        if matching_windows:
            # Format results
            message = f"🔍 Found {len(matching_windows)} window(s) starting with '{search_term}':\n\n"
            
            for i, (hwnd, title) in enumerate(matching_windows, 1):
                # Get additional window info
                from utils.windows_automation import get_window_info
                window_info = get_window_info(hwnd)
                
                message += f"{i}. Title: {title}\n"
                message += f"   Handle: {hwnd}\n"
                
                if window_info:
                    message += f"   Position: ({window_info['left']}, {window_info['top']})\n"
                    message += f"   Size: {window_info['width']}x{window_info['height']}\n"
                    message += f"   Visible: {window_info['is_visible']}\n"
                    message += f"   Minimized: {window_info['is_minimized']}\n"
                    message += f"   Maximized: {window_info['is_maximized']}\n"
                
                message += "\n"
                show_result_dialog(root, message)           
        else:
            messagebox.showinfo(
                "Search Results", 
                f"No windows found starting with '{search_term}'"
            )
    
    except Exception as e:
        messagebox.showerror("Error", f"Error searching for windows:\n\n{str(e)}")

def test_automation():
    """Test general automation functionality"""
    if not PYWIN32_AVAILABLE:
        messagebox.showerror("Error", "pywin32 is required for Windows automation.\n\nPlease install it using:\npip install pywin32")
        return
    
    try:
        # Test by listing available windows
        from utils.windows_automation import list_all_windows
        windows = list_all_windows()
        
        message = f"✅ Automation Test Results:\n\n"
        message += f"pywin32: Available ✅\n"
        message += f"pynput: {'Available ✅' if PYNPUT_AVAILABLE else 'Not Available ❌'}\n"
        message += f"Total windows found: {len(windows)}\n\n"
        message += "Sample windows:\n"
        
        # Show first 5 windows as sample
        for i, (hwnd, title) in enumerate(windows[:5], 1):
            message += f"{i}. {title} (Handle: {hwnd})\n"
        
        if len(windows) > 5:
            message += f"... and {len(windows) - 5} more windows"
        
        messagebox.showinfo("Automation Test", message)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error testing automation:\n\n{str(e)}")

def run_notepad_automation():
    """Run the Notepad automation script"""
    try:
        import subprocess
        import os
        
        # Get the path to the notepad automation script
        script_path = os.path.join(os.path.dirname(__file__), "automation", "notepad", "notepad.py")
        
        if os.path.exists(script_path):
            print("🚀 Running Notepad automation...")
            # Run the script in a separate process and track it
            process = subprocess.Popen([sys.executable, script_path], 
                                     cwd=os.path.dirname(__file__))
            spawned_processes.append(process)
            print(f"   • Process started with PID: {process.pid}")
            # messagebox.showinfo("Automation Started", "Notepad automation script has been launched!")
        else:
            messagebox.showerror("Error", f"Notepad automation script not found at:\n{script_path}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run Notepad automation:\n\n{str(e)}")

def toggle_btt_automation():
    """Toggle BTT automation - start if stopped, stop if running"""
    global btt_process, btt_button
    
    # Check if BTT is currently running
    if btt_process and btt_process.poll() is None:
        # BTT is running, stop it
        print("🛑 Stopping BTT automation...")
        try:
            btt_process.terminate()
            try:
                btt_process.wait(timeout=2)
                print(f"   ✅ BTT process {btt_process.pid} terminated gracefully")
            except subprocess.TimeoutExpired:
                print(f"   🔪 Force killing BTT process {btt_process.pid}")
                btt_process.kill()
                btt_process.wait()
                print(f"   ✅ BTT process {btt_process.pid} force killed")
            
            # Remove from spawned_processes list
            if btt_process in spawned_processes:
                spawned_processes.remove(btt_process)
            
        except (ProcessLookupError, PermissionError):
            print("   ⚠️ BTT process already terminated")
        except Exception as e:
            print(f"   ❌ Error stopping BTT: {e}")
        
        # Reset process and update button
        btt_process = None
        btt_button.config(text="BTT", bg="#D35400")
        print("   ✅ BTT stopped, button reset")
        
    else:
        # BTT is not running, start it
        try:
            import subprocess
            import os
            
            script_path = os.path.join(os.path.dirname(__file__), "automation", "btt", "btt.py")
            
            if os.path.exists(script_path):
                print("🚀 Starting BTT automation...")
                btt_process = subprocess.Popen([sys.executable, script_path], 
                                             cwd=os.path.dirname(__file__))
                spawned_processes.append(btt_process)
                print(f"   • BTT process started with PID: {btt_process.pid}")
                
                # Update button to show stop option
                btt_button.config(text="Stop BTT", bg="#E74C3C")
                print("   ✅ BTT started, button updated")
            else:
                messagebox.showerror("Error", f"BTT automation script not found at:\n{script_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start BTT automation:\n\n{str(e)}")

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
        "• The window will hide to avoid interference"
    )
    
    # Store current window geometry before hiding
    global window_geometry
    window_geometry = root.geometry()
    
    # Hide the main window (can't use iconify with overrideredirect=True)
    root.withdraw()
    
    # Start recording
    recorder.start_recording()
    
    # Poll for recording completion from main thread
    def check_recording_status():
        if recorder.recording:
            # Still recording, check again in 100ms
            root.after(100, check_recording_status)
        else:
            # Recording stopped, finish up
            finish_recording()
    
    # Start polling
    root.after(100, check_recording_status)

def get_suggested_sequence_name():
    """Get a unique suggested name for the sequence using utility"""
    return generate_suggested_name()

def kill_all_spawned_processes():
    """Force kill all spawned processes"""
    global spawned_processes
    killed_count = 0
    
    for process in spawned_processes[:]:  # Create a copy to iterate over
        try:
            if process.poll() is None:  # Process is still running
                print(f"   • Terminating process PID: {process.pid}")
                process.terminate()
                
                # Wait up to 2 seconds for graceful termination
                try:
                    process.wait(timeout=2)
                    print(f"     ✅ Process {process.pid} terminated gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    print(f"     🔪 Force killing process {process.pid}")
                    process.kill()
                    process.wait()  # Clean up zombie
                    print(f"     ✅ Process {process.pid} force killed")
                
                killed_count += 1
            else:
                print(f"   • Process PID {process.pid} already terminated")
            
            spawned_processes.remove(process)
            
        except (ProcessLookupError, PermissionError) as e:
            print(f"   ⚠️ Process {process.pid} already gone: {e}")
            try:
                spawned_processes.remove(process)
            except ValueError:
                pass
        except Exception as e:
            print(f"   ❌ Error killing process {process.pid}: {e}")
    
    if killed_count > 0:
        print(f"   • Successfully terminated {killed_count} processes")
    else:
        print("   • No active processes to terminate")

def on_closing():
    """Handle window closing - THE ULTIMATE SHUTDOWN BUTTON"""
    global recorder, root, shutdown_in_progress
    
    # Prevent multiple shutdown attempts
    if shutdown_in_progress:
        return
        
    shutdown_in_progress = True
    
    # Prevent double-destroy
    if not root or not root.winfo_exists():
        return
    
    print("\n🛑 ULTIMATE SHUTDOWN INITIATED...")
    print("   🔪 This will terminate ALL operations immediately!")
    
    try:
        # Stop any active recording
        if 'recorder' in globals() and recorder and recorder.recording:
            print("   • Stopping active recording...")
            try:
                recorder.stop_recording()
                print("     ✅ Recording stopped")
            except Exception as e:
                print(f"     ⚠️ Error stopping recording: {e}")
        
        # Kill all spawned automation processes
        print("   • Terminating all spawned automation processes...")
        kill_all_spawned_processes()
        
        # Stop any mouse/keyboard listeners that might still be running
        try:
            if 'recorder' in globals() and recorder and hasattr(recorder, 'mouse_listener') and recorder.mouse_listener:
                recorder.mouse_listener.stop()
            if 'recorder' in globals() and recorder and hasattr(recorder, 'keyboard_listener') and recorder.keyboard_listener:
                recorder.keyboard_listener.stop()
            print("   • Input listeners stopped")
        except Exception as e:
            print(f"     ⚠️ Error stopping listeners: {e}")
        
        print("✅ COMPLETE SHUTDOWN SUCCESSFUL!")
        
    except Exception as e:
        print(f"⚠️ Warning during shutdown: {e}")
        print("🔪 Forcing immediate exit anyway...")
    
    # Destroy the GUI
    try:
        root.quit()  # Exit the mainloop
        root.destroy()  # Destroy the window
    except tk.TclError:
        # Already destroyed, that's fine
        pass
    
    # Force exit to ensure everything is terminated
    print("🛑 Forcing immediate exit...")
    os._exit(0)  # Nuclear option - immediately terminate the entire process

def signal_handler(signum, frame):
    """Handle Ctrl+C and other signals - immediate shutdown"""
    print(f"\n🔄 Received signal {signum}, triggering ultimate shutdown...")
    on_closing()  # Use the same comprehensive shutdown logic

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
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Fiserv Automation Taskbar...")
    print("💡 Press Ctrl+C anytime for graceful shutdown")
    
    # Create the main window
    root = tk.Tk()
    root.title("Fiserv Automation Taskbar")
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Configure taskbar dimensions
    taskbar_height = 60
    taskbar_width = screen_width
    
    # Position at top of screen
    root.geometry(f"{taskbar_width}x{taskbar_height}+0+0")
    root.resizable(False, False)
    
    # Configure window to stay on top and remove decorations
    root.attributes('-topmost', True)
    root.overrideredirect(True)  # Remove title bar completely
    
    # Configure root background
    root.configure(bg='#2C3E50')
    
    # Create main horizontal frame for all controls
    main_frame = tk.Frame(root, bg='#2C3E50', height=taskbar_height)
    main_frame.pack(fill=tk.BOTH, expand=True)
    main_frame.pack_propagate(False)
    
    # Left section: Title
    title_frame = tk.Frame(main_frame, bg='#2C3E50')
    title_frame.pack(side=tk.LEFT, padx=10, pady=5)
    
    title_label = tk.Label(
        title_frame,
        text="Fiserv Automation",
        font=("Arial", 14, "bold"),
        fg="white",
        bg='#2C3E50'
    )
    title_label.pack(anchor='w')
    
    # Center section: Main buttons
    buttons_frame = tk.Frame(main_frame, bg='#2C3E50')
    buttons_frame.pack(side=tk.LEFT, padx=20, pady=5, expand=True)
    
    # Button styling
    button_style = {
        'font': ("Arial", 10, "bold"),
        'fg': "white",
        'relief': 'flat',
        'cursor': 'hand2',
        'height': 2
    }
    
    # Create all main buttons horizontally
    # scan_button = tk.Button(
    #     buttons_frame,
    #     text="Scan Image",
    #     command=scan_image,
    #     bg="#27AE60",
    #     width=12,
    #     **button_style
    # )
    # scan_button.pack(side=tk.LEFT, padx=2)
    
    # advanced_scan_button = tk.Button(
    #     buttons_frame,
    #     text="Advanced Scan",
    #     command=scan_image_advanced,
    #     bg="#8E44AD",
    #     width=12,
    #     **button_style
    # )
    # advanced_scan_button.pack(side=tk.LEFT, padx=2)
    
    record_button = tk.Button(
        buttons_frame,
        text="Record Sequence",
        command=record_sequence,
        bg="#E67E22",
        width=14,
        **button_style
    )
    record_button.pack(side=tk.LEFT, padx=2)
    
    # test_automation_button = tk.Button(
    #     buttons_frame,
    #     text="Test Automation",
    #     command=test_automation,
    #     bg="#3498DB",
    #     width=14,
    #     **button_style
    # )
    # test_automation_button.pack(side=tk.LEFT, padx=2)
    
    search_window_button = tk.Button(
        buttons_frame,
        text="Search Window",
        command=search_window,
        bg="#9B59B6",
        width=13,
        **button_style
    )
    search_window_button.pack(side=tk.LEFT, padx=2)
    
    # Automation buttons
    # notepad_button = tk.Button(
    #     buttons_frame,
    #     text="Notepad Test",
    #     command=run_notepad_automation,
    #     bg="#16A085",
    #     width=12,
    #     **button_style
    # )
    # notepad_button.pack(side=tk.LEFT, padx=2)
    
    # Make btt_button global so toggle function can access it
    global btt_button
    btt_button = tk.Button(
        buttons_frame,
        text="BTT",
        command=toggle_btt_automation,
        bg="#D35400",
        width=10,
        **button_style
    )
    btt_button.pack(side=tk.LEFT, padx=2)
    
    # Right section: Status and Exit
    right_frame = tk.Frame(main_frame, bg='#2C3E50')
    right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    # Status indicator (compact)
    status_color = "#27AE60" if PYNPUT_AVAILABLE and PYWIN32_AVAILABLE else "#E74C3C"
    status_text = "●" if PYNPUT_AVAILABLE and PYWIN32_AVAILABLE else "●"
    
    status_label = tk.Label(
        right_frame,
        text=status_text,
        font=("Arial", 16),
        fg=status_color,
        bg='#2C3E50'
    )
    status_label.pack(side=tk.LEFT, padx=5)
    
    # Exit button
    exit_button = tk.Button(
        right_frame,
        text="✕",
        command=on_closing,
        font=("Arial", 12, "bold"),
        bg="#E74C3C",
        fg="white",
        relief='flat',
        width=2,
        height=1,
        cursor='hand2'
    )
    exit_button.pack(side=tk.LEFT, padx=5)
    
    # Add tooltips/hover effects
    def on_enter(event, button, hover_color):
        button.config(bg=hover_color)
    
    def on_leave(event, button, original_color):
        button.config(bg=original_color)
    
    # Bind hover effects
    buttons_config = [
        # (scan_button, "#27AE60", "#2ECC71"),
        # (advanced_scan_button, "#8E44AD", "#9B59B6"),
        (record_button, "#E67E22", "#F39C12"),
        # (test_automation_button, "#3498DB", "#5DADE2"),
        (search_window_button, "#9B59B6", "#AF7AC5"),
        # (notepad_button, "#16A085", "#1ABC9C"),
        (btt_button, "#D35400", "#E67E22"),
        (exit_button, "#E74C3C", "#EC7063")
    ]
    
    for button, original, hover in buttons_config:
        button.bind("<Enter>", lambda e, b=button, h=hover: on_enter(e, b, h))
        button.bind("<Leave>", lambda e, b=button, o=original: on_leave(e, b, o))
    
    # Set up window close protocol (even though we removed title bar)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Make window focusable for keyboard events
    root.focus_set()
    
    # Bind Ctrl+C directly to the window as backup
    root.bind('<Control-c>', lambda e: on_closing())
    
    # BTT process monitoring function
    def monitor_btt_process():
        """
        Monitor BTT subprocess status and keep GUI button state synchronized.
        
        WHY THIS IS NEEDED:
        - BTT runs as a separate subprocess (launched via subprocess.Popen)
        - When BTT hits a critical exception, it calls sys.exit(1) and terminates
        - The parent GUI process has NO direct notification when subprocess dies
        - Without monitoring, button would show "Stop BTT" even when process is dead
        - User would see inconsistent state: button says "running" but process is dead
        
        WHY THIS APPROACH:
        - Subprocess isolation prevents direct callbacks/notifications
        - Inter-process communication (IPC) would add complexity (pipes, shared memory)
        - File-based flags would be slower and add filesystem I/O
        - Simple polling every 50ms is lightweight and reliable
        - poll() method is non-blocking and efficient for checking process status
        
        TECHNICAL FLOW:
        1. User clicks BTT → subprocess starts → button shows "Stop BTT" (red)
        2. BTT hits critical exception → subprocess calls sys.exit(1) → dies
        3. This monitor detects death via poll() → resets button to "BTT" (orange)
        4. GUI state stays perfectly synchronized with actual process state
        
        FUTURE MAINTENANCE:
        - If you see button sync issues, check this monitoring function
        - The 50ms interval balances responsiveness vs CPU usage
        - Only runs when button shows "Stop BTT" to minimize overhead
        """
        global btt_process, btt_button
        
        # Only check if we think BTT is running (button shows "Stop BTT")
        if (btt_process is not None and 
            btt_button.cget("text") == "Stop BTT" and 
            btt_process.poll() is not None):
            
            # Process has terminated but button still shows "Stop BTT"
            print(f"🔄 BTT process {btt_process.pid} has terminated, syncing button state...")
            
            # Remove from spawned_processes list
            if btt_process in spawned_processes:
                spawned_processes.remove(btt_process)
            
            # Reset process and update button
            btt_process = None
            btt_button.config(text="BTT", bg="#D35400")
            print("   ✅ Button synced back to 'BTT' state")
    
    print("✅ Taskbar ready! All systems operational.")
    
    # Custom mainloop for responsive Ctrl+C (but keep it simple)
    try:
        while True:
            root.update()
            # CRITICAL: Monitor BTT subprocess and sync button state
            # This ensures GUI button accurately reflects actual process status
            # See monitor_btt_process() docstring for full technical explanation
            monitor_btt_process()  
            time.sleep(0.05)  # 50ms - good balance between responsiveness and CPU usage
    except tk.TclError:
        # Window was closed normally
        pass
    except KeyboardInterrupt:
        # Ctrl+C pressed
        on_closing()

if __name__ == "__main__":
    main() 