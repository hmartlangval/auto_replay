"""Auto-generated sequence: my_sequence"""
# Generated on: 2025-06-25 00:15:37
# Screen Resolution: 1536x864
# DPI: 120x120 (Scale: 1.2x)
# Platform: Windows
import time
import tkinter as tk
from tkinter import messagebox
import platform
try:
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    import pynput.mouse as mouse_control
    import pynput.keyboard as keyboard_control
except ImportError:
    print("pynput library required. Install with: pip install pynput")
    exit(1)

# Windows-specific imports for DPI detection
if platform.system() == "Windows":
    try:
        import ctypes
        WINDOWS_DPI_AVAILABLE = True
    except ImportError:
        WINDOWS_DPI_AVAILABLE = False
else:
    WINDOWS_DPI_AVAILABLE = False
def get_current_screen_info():
    """Get current screen resolution and DPI information"""
    screen_info = {}
    
    # Get screen resolution
    try:
        temp_root = tk.Tk()
        temp_root.withdraw()
        screen_info["width"] = temp_root.winfo_screenwidth()
        screen_info["height"] = temp_root.winfo_screenheight()
        temp_root.destroy()
    except:
        screen_info["width"] = 1920
        screen_info["height"] = 1080
    
    # Get DPI information (Windows)
    if WINDOWS_DPI_AVAILABLE:
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            dc = user32.GetDC(0)
            dpi_x = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)
            dpi_y = ctypes.windll.gdi32.GetDeviceCaps(dc, 90)
            user32.ReleaseDC(0, dc)
            screen_info["dpi_x"] = dpi_x
            screen_info["dpi_y"] = dpi_y
            screen_info["dpi_scale"] = dpi_x / 96.0
        except:
            screen_info["dpi_x"] = 96
            screen_info["dpi_y"] = 96
            screen_info["dpi_scale"] = 1.0
    
    screen_info["platform"] = platform.system()
    return screen_info
def validate_screen_compatibility():
    """Check if current screen settings match recorded settings"""
    recorded_settings = {
        "width": 1536,
        "height": 864,
        "dpi_x": 120,
        "dpi_y": 120,
        "dpi_scale": 1.25,
        "platform": "Windows"
    }
    
    current_settings = get_current_screen_info()
    
    mismatches = []
    if current_settings["width"] != recorded_settings["width"] or current_settings["height"] != recorded_settings["height"]:
        res_msg = f"Resolution: Recorded {recorded_settings['width']}x{recorded_settings['height']}, Current {current_settings['width']}x{current_settings['height']}"
        mismatches.append(res_msg)
    
    if abs(current_settings["dpi_scale"] - recorded_settings["dpi_scale"]) > 0.1:
        dpi_msg = f"DPI Scale: Recorded {recorded_settings['dpi_scale']:.1f}x, Current {current_settings['dpi_scale']:.1f}x"
        mismatches.append(dpi_msg)
    
    if current_settings["platform"] != recorded_settings["platform"]:
        platform_msg = f"Platform: Recorded {recorded_settings['platform']}, Current {current_settings['platform']}"
        mismatches.append(platform_msg)
    
    return mismatches
def replay_my_sequence():
    """Replay the recorded sequence"""
    # Validate screen compatibility first
    mismatches = validate_screen_compatibility()
    if mismatches:
        error_msg = "Screen settings mismatch detected!\n\n"
        error_msg += "This sequence was recorded with different screen settings:\n"
        for mismatch in mismatches:
            error_msg += f"• {mismatch}\n"
        error_msg += "\nReplaying with different settings may cause clicks to miss their targets.\n"
        error_msg += "Please adjust your screen settings to match the recorded ones, or re-record the sequence."
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Screen Settings Mismatch", error_msg)
            root.destroy()
        except:
            print("ERROR: " + error_msg.replace("\n", " "))
        return False
    
    mouse = mouse_control.Controller()
    keyboard = keyboard_control.Controller()
    
    print(f"Starting replay of sequence: my_sequence")
    print("Screen settings validated successfully!")
    
    time.sleep(1.04)  # Wait 1.04s
    # Mouse click at (1506, 754)
    mouse.position = (1506, 754)
    mouse.click(Button.left)

    time.sleep(0.48)  # Wait 0.48s
    # Mouse click at (1636, 739)
    mouse.position = (1636, 739)
    mouse.click(Button.left)

    time.sleep(1.33)  # Wait 1.33s
    # Mouse click at (753, 266)
    mouse.position = (753, 266)
    mouse.click(Button.left)

    time.sleep(0.41)  # Wait 0.41s
    # Mouse click at (503, 239)
    mouse.position = (503, 239)
    mouse.click(Button.left)

    print("Sequence replay completed successfully!")
    return True
if __name__ == "__main__":
    success = replay_my_sequence()
    if not success:
        print("Replay failed due to screen settings mismatch.")
        exit(1)