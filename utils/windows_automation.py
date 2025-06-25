
"""
Windows automation utilities for targeting and controlling specific windows
Provides functionality to find windows, bring them to focus, and perform automation tasks
"""
import time
import win32gui
import win32api
import win32con
from typing import List, Tuple, Optional


def list_all_windows() -> List[Tuple[int, str]]:
    """
    List all visible windows with their handles and titles.
    
    Returns:
        List[Tuple[int, str]]: List of (window_handle, target_window_title) tuples
    """
    windows = []
    
    def enum_handler(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            target_window_title = win32gui.GetWindowText(hwnd)
            if target_window_title:  # Only include windows with titles
                results.append((hwnd, target_window_title))
    
    win32gui.EnumWindows(enum_handler, windows)
    return windows


def find_windows_by_title(partial_title: str) -> List[Tuple[int, str]]:
    """
    Find windows containing the specified text in their title.
    
    Args:
        partial_title: Partial window title to search for (case-insensitive)
        
    Returns:
        List[Tuple[int, str]]: List of matching (window_handle, target_window_title) tuples
    """
    all_windows = list_all_windows()
    matching_windows = []
    
    for hwnd, title in all_windows:
        if partial_title.lower() in title.lower():
            matching_windows.append((hwnd, title))
    
    return matching_windows


def find_windows_by_title_starts_with(prefix: str) -> List[Tuple[int, str]]:
    """
    Find windows whose title starts with the specified text.
    This handles both main parent windows and Win32 modal dialogs.
    
    Args:
        prefix: Text that window title should start with (case-insensitive)
        
    Returns:
        List[Tuple[int, str]]: List of matching (window_handle, target_window_title) tuples
    """
    all_windows = list_all_windows()
    matching_windows = []
    
    for hwnd, title in all_windows:
        if title.lower().startswith(prefix.lower()):
            matching_windows.append((hwnd, title))
    
    return matching_windows


def get_window_info(hwnd: int) -> Optional[dict]:
    """
    Get detailed information about a window.
    
    Args:
        hwnd: Window handle
        
    Returns:
        dict: Window information including title, position, size, visibility
    """
    try:
        if not win32gui.IsWindow(hwnd):
            return None
        
        # Get basic window information with error handling
        try:
            title = win32gui.GetWindowText(hwnd)
        except:
            title = "Unknown"
            
        try:
            rect = win32gui.GetWindowRect(hwnd)
        except:
            rect = (0, 0, 0, 0)
            
        try:
            is_visible = win32gui.IsWindowVisible(hwnd)
        except:
            is_visible = False
            
        try:
            is_minimized = win32gui.IsIconic(hwnd)
        except:
            is_minimized = False
        
        # Check if window is maximized using GetWindowPlacement
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            # placement[1] is the showCmd, SW_SHOWMAXIMIZED = 3
            # Use the constant if available, otherwise use the raw value
            try:
                sw_maximized = win32con.SW_SHOWMAXIMIZED
            except AttributeError:
                sw_maximized = 3  # SW_SHOWMAXIMIZED constant value
            
            is_maximized = (placement[1] == sw_maximized)
        except:
            # Fallback: compare window rect with screen size
            try:
                import tkinter as tk
                temp_root = tk.Tk()
                temp_root.withdraw()
                screen_width = temp_root.winfo_screenwidth()
                screen_height = temp_root.winfo_screenheight()
                temp_root.destroy()
                
                window_width = rect[2] - rect[0]
                window_height = rect[3] - rect[1]
                # Consider maximized if window covers most of screen
                is_maximized = (window_width >= screen_width * 0.95 and 
                              window_height >= screen_height * 0.95)
            except:
                is_maximized = False
        
        return {
            'handle': hwnd,
            'title': title,
            'left': rect[0],
            'top': rect[1],
            'right': rect[2],
            'bottom': rect[3],
            'width': rect[2] - rect[0],
            'height': rect[3] - rect[1],
            'is_visible': is_visible,
            'is_minimized': is_minimized,
            'is_maximized': is_maximized
        }
    except Exception as e:
        print(f"Error getting window info for handle {hwnd}: {e}")
        return None


class ManualAutomationHelper:
    def __init__(self, window_handle=None, target_window_title=None, title_starts_with=False):
        """
        Initialize the helper with window information.
        
        Args:
            window_handle: Direct window handle (HWND)
            target_window_title: Window title to find the handle
        """
        if window_handle:
            self.hwnd = window_handle
        elif target_window_title:
            if title_starts_with:
                self.hwnd = find_windows_by_title_starts_with(target_window_title)
            else:
                self.hwnd = win32gui.FindWindow(None, target_window_title)
            if not self.hwnd:
                raise ValueError(f"Window not found: '{target_window_title}'")
        else:
            raise ValueError("Either window_handle or target_window_title must be provided")
        
        self.target_window_title = target_window_title or self._get_target_window_title()
        
        # Initialize bbox with current window rect as default
        self._bring_to_focus()
        self._initialize_default_bbox()
    
    def _get_target_window_title(self):
        """Get window title from handle."""
        try:
            return win32gui.GetWindowText(self.hwnd)
        except:
            return "Unknown"
    
    def _initialize_default_bbox(self):
        """Initialize default bounding box from current window rect."""
        try:
            if win32gui.IsWindow(self.hwnd):
                rect = win32gui.GetWindowRect(self.hwnd)
                # Store as (left, top, right, bottom) tuple
                self.bbox = rect
                print(f"Default bbox initialized: {self.bbox}")
            else:
                # Fallback bbox if window is not valid
                self.bbox = (56, 37, 985, 609)
                print(f"Using fallback bbox: {self.bbox}")
        except Exception as e:
            # Fallback bbox on error
            self.bbox = (56, 37, 985, 609)
            print(f"Error initializing bbox, using fallback: {e}")
    
    def set_bbox(self, left, top, right, bottom):
        """
        Set the bounding box for window operations.
        
        Args:
            left: Left coordinate
            top: Top coordinate
            right: Right coordinate
            bottom: Bottom coordinate
        """
        self.bbox = (left, top, right, bottom)
        print(f"Bbox updated to: {self.bbox}")
    
    def get_bbox(self):
        """Get the current bounding box."""
        return self.bbox
    
    def get_bbox_dimensions(self):
        """
        Get the width and height of the current bounding box.
        
        Returns:
            tuple: (width, height)
        """
        left, top, right, bottom = self.bbox
        return (right - left, bottom - top)
    
    def get_bbox_center(self):
        """
        Get the center point of the current bounding box.
        
        Returns:
            tuple: (center_x, center_y)
        """
        left, top, right, bottom = self.bbox
        center_x = left + (right - left) // 2
        center_y = top + (bottom - top) // 2
        return (center_x, center_y)
    
    def is_point_in_bbox(self, x, y):
        """
        Check if a point is within the current bounding box.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if point is within bbox
        """
        left, top, right, bottom = self.bbox
        return left <= x <= right and top <= y <= bottom
    
    def _bring_to_focus(self, hwnd=None):
        """Bring the target window to focus."""
        try:
            # Show window if minimized
            win32gui.ShowWindow(hwnd or self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd or self.hwnd)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"Warning: Could not bring window to focus: {e}")
            return False

    def setup_window_by_handle(self, hwnd=int, bbox=tuple):
        """
        Setup the target application window.
        
        Args:
            bbox: Optional bounding box as (left, top, right, bottom) tuple.
                  If provided, updates self.bbox and uses it for window positioning.
                  If None, uses current self.bbox.
        """
        print("Setting up target window...")
        
        try:
            if not hwnd:
                print(f"❌ Handle is not provided")
                return False
            
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            print("✅ Window brought to focus")
            
            # Resize and position window using self.bbox
            target_left, target_top, target_right, target_bottom = bbox
            
            width = target_right - target_left
            height = target_bottom - target_top
            
            win32gui.MoveWindow(hwnd, target_left, target_top, width, height, True)
            time.sleep(0.2)
            
            # Verify positioning
            current_rect = win32gui.GetWindowRect(hwnd)
            print(f"✅ Window repositioned:")
            print(f"   Target: Left:{target_left} Top:{target_top} Right:{target_right} Bottom:{target_bottom}")
            print(f"   Actual: Left:{current_rect[0]} Top:{current_rect[1]} Right:{current_rect[2]} Bottom:{current_rect[3]}")
            
            print("🎉 Window setup completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up window: {e}")
            return False
     
    def setup_window(self, bbox=None, hwnd=None):
        """
        Setup the target application window.
        
        Args:
            bbox: Optional bounding box as (left, top, right, bottom) tuple.
                  If provided, updates self.bbox and uses it for window positioning.
                  If None, uses current self.bbox.
        """
        print("Setting up target window...")
        
        try:
            # Find target window
            hwnd = win32gui.FindWindow(None, self.target_window_title)
            if not hwnd:
                print(f"❌ Window not found: '{self.target_window_title}'")
                return False
            
            self.target_hwnd = hwnd
            print(f"✅ Found window: '{self.target_window_title}' (Handle: {hwnd})")
            
            # Update bbox if provided
            if bbox is not None:
                if len(bbox) == 4:
                    self.bbox = bbox
                    print(f"✅ Bbox updated to: {self.bbox}")
                else:
                    print("⚠️ Warning: Invalid bbox format. Expected (left, top, right, bottom)")
            
            # Bring to focus
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            print("✅ Window brought to focus")
            
            # Resize and position window using self.bbox
            target_left, target_top, target_right, target_bottom = self.bbox
            
            width = target_right - target_left
            height = target_bottom - target_top
            
            win32gui.MoveWindow(hwnd, target_left, target_top, width, height, True)
            time.sleep(0.2)
            
            # Verify positioning
            current_rect = win32gui.GetWindowRect(hwnd)
            print(f"✅ Window repositioned:")
            print(f"   Target: Left:{target_left} Top:{target_top} Right:{target_right} Bottom:{target_bottom}")
            print(f"   Actual: Left:{current_rect[0]} Top:{current_rect[1]} Right:{current_rect[2]} Bottom:{current_rect[3]}")
            
            print("🎉 Window setup completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up window: {e}")
            return False
            
    def type(self, text, hwnd=None):
        """
        Type text into the focused window.
        
        Args:
            text: Text string to type
            
        Returns:
            bool: Success status
        """
        try:
            # Bring window to focus
            self._bring_to_focus(hwnd)
            
            # Type each character
            for char in text:
                # Get virtual key code for character
                vk_code = win32api.VkKeyScan(char)
                if vk_code == -1:
                    # Character not available, skip
                    continue
                
                # Extract key code and shift state
                key_code = vk_code & 0xFF
                shift_state = (vk_code >> 8) & 0xFF
                
                # Press shift if needed
                if shift_state & 1:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                
                # Press and release the key
                win32api.keybd_event(key_code, 0, 0, 0)
                win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                # Release shift if pressed
                if shift_state & 1:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.01)  # Small delay between keystrokes
            
            return True
            
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def click(self, coordinate):
        """
        Click at the specified coordinate.
        
        Args:
            coordinate: Tuple (x, y) of screen coordinates
            
        Returns:
            bool: Success status
        """
        try:
            # Bring window to focus
            self._bring_to_focus()
            
            x, y = coordinate
            
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            
            # Perform left click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            
            return True
            
        except Exception as e:
            print(f"Error clicking at {coordinate}: {e}")
            return False
    
    def keys(self, key_combination, hwnd=None):
        """
        Send key combination with modifiers.
        
        Args:
            key_combination: String with modifiers in curly braces
                           Examples: "{Ctrl+F}", "{Enter}", "{Alt+Tab}", "text"
                           
        Returns:
            bool: Success status
        """
        try:
            
            if not hwnd:
                hwnd = self.hwnd
                # Bring window to focus
            self._bring_to_focus(hwnd)
            
            # Parse key combination
            if key_combination.startswith('{') and key_combination.endswith('}'):
                # Special key combination
                keys_str = key_combination[1:-1]  # Remove braces
                
                # Parse modifiers and key
                modifiers = []
                main_key = keys_str
                
                if '+' in keys_str:
                    parts = keys_str.split('+')
                    modifiers = [part.strip() for part in parts[:-1]]
                    main_key = parts[-1].strip()
                
                # Press modifiers
                modifier_codes = []
                for modifier in modifiers:
                    if modifier.lower() == 'ctrl':
                        modifier_codes.append(win32con.VK_CONTROL)
                        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    elif modifier.lower() == 'alt':
                        modifier_codes.append(win32con.VK_MENU)
                        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                    elif modifier.lower() == 'shift':
                        modifier_codes.append(win32con.VK_SHIFT)
                        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                    elif modifier.lower() == 'win':
                        modifier_codes.append(win32con.VK_LWIN)
                        win32api.keybd_event(win32con.VK_LWIN, 0, 0, 0)
                
                time.sleep(0.05)
                
                # Press main key
                main_vk = self._get_virtual_key_code(main_key)
                if main_vk:
                    win32api.keybd_event(main_vk, 0, 0, 0)
                    win32api.keybd_event(main_vk, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.05)
                
                # Release modifiers in reverse order
                for modifier_code in reversed(modifier_codes):
                    win32api.keybd_event(modifier_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            else:
                # Regular text, use type function
                return self.type(key_combination)
            
            return True
            
        except Exception as e:
            print(f"Error sending keys '{key_combination}': {e}")
            return False
    
    def _get_virtual_key_code(self, key_name):
        """Get virtual key code for special keys."""
        special_keys = {
            'enter': win32con.VK_RETURN,
            'tab': win32con.VK_TAB,
            'space': win32con.VK_SPACE,
            'backspace': win32con.VK_BACK,
            'delete': win32con.VK_DELETE,
            'escape': win32con.VK_ESCAPE,
            'esc': win32con.VK_ESCAPE,
            'home': win32con.VK_HOME,
            'end': win32con.VK_END,
            'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT,
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
            'f1': win32con.VK_F1,
            'f2': win32con.VK_F2,
            'f3': win32con.VK_F3,
            'f4': win32con.VK_F4,
            'f5': win32con.VK_F5,
            'f6': win32con.VK_F6,
            'f7': win32con.VK_F7,
            'f8': win32con.VK_F8,
            'f9': win32con.VK_F9,
            'f10': win32con.VK_F10,
            'f11': win32con.VK_F11,
            'f12': win32con.VK_F12,
        }
        
        key_lower = key_name.lower()
        if key_lower in special_keys:
            return special_keys[key_lower]
        
        # For single characters, try VkKeyScan
        if len(key_name) == 1:
            vk_code = win32api.VkKeyScan(key_name)
            if vk_code != -1:
                return vk_code & 0xFF
        
        return None
    
    def get_window_info(self):
        """Get detailed information about the target window."""
        return get_window_info(self.hwnd)
    
    def is_window_valid(self):
        """Check if the window handle is still valid."""
        try:
            return win32gui.IsWindow(self.hwnd)
        except:
            return False
    
    def get_window_rect(self):
        """Get window rectangle coordinates."""
        try:
            return win32gui.GetWindowRect(self.hwnd)
        except Exception as e:
            print(f"Error getting window rect: {e}")
            return None
    
    def move_window(self, x, y, width, height):
        """
        Move and resize the window.
        
        Args:
            x: New x position
            y: New y position  
            width: New width
            height: New height
            
        Returns:
            bool: Success status
        """
        try:
            win32gui.MoveWindow(self.hwnd, x, y, width, height, True)
            return True
        except Exception as e:
            print(f"Error moving window: {e}")
            return False
    
    def minimize_window(self):
        """Minimize the window."""
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            print(f"Error minimizing window: {e}")
            return False
    
    def maximize_window(self):
        """Maximize the window."""
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            print(f"Error maximizing window: {e}")
            return False
    
    def restore_window(self):
        """Restore the window from minimized/maximized state."""
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            return True
        except Exception as e:
            print(f"Error restoring window: {e}")
            return False
