"""
TreeView Navigator - Console interface for navigating real UI treeviews
using smart expand/collapse navigation with keyboard automation.
"""

import time
import sys
import os
from typing import List, Optional

# Add parent directory to path for imports when running directly
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from windows_automation import ManualAutomationHelper
    from treeview_path_computer import TreeviewPathComputer
else:
    from ..windows_automation import ManualAutomationHelper
    from .treeview_path_computer import TreeviewPathComputer


class TreeViewNavigator:
    """
    Smart tree navigator that sends keyboard keys to real UI treeview controls.
    Uses TreeviewPathComputer for logic and executes the key sequences.
    """
    
    def __init__(self, automation_helper: ManualAutomationHelper = None, window_title: str = None, collapse_count: int = 1):
        """
        Initialize the navigator for a specific window containing a treeview.
        
        Args:
            automation_helper: Pre-initialized automation helper
            window_title: Title of the window containing the treeview
            collapse_count: Number of left arrows needed to collapse a node (default: 1)
        """
        self.automation = automation_helper
        self.current_path = "1"  # Root is now level 1
        self.collapse_count = collapse_count  # How many left arrows for collapse
        self.path_computer = TreeviewPathComputer()
        self.first_navigation = True  # Flag to track if this is the first navigation
        
        if automation_helper is None and window_title:
            self.connect_to_window(window_title)
    
    def connect_to_window(self, window_title: str) -> bool:
        """Connect to a window containing a treeview."""
        try:
            self.automation = ManualAutomationHelper(target_window_title=window_title)
            print(f"✅ Connected to window: {self.automation.target_window_title}")
            self.current_path = "1"  # Reset to root level 1
            return True
        except Exception as e:
            print(f"❌ Error connecting to window: {e}")
            return False
    
    def send_key(self, key: str, delay: float = None) -> bool:
        """
        Send a key to the target window.
        
        Args:
            key: Key to send (e.g., "Up", "Down", "Left", "Right")
            delay: Custom delay after key press
            
        Returns:
            True if successful, False otherwise
        """
        if not self.automation:
            print("❌ Not connected to any window")
            return False
        
        try:
            # Convert key names to proper format for automation
            key_map = {
                "Up": "{Up}",
                "Down": "{Down}",
                "Left": "{Left}",
                "Right": "{Right}"
            }
            
            formatted_key = key_map.get(key, key)
            success = self.automation.keys(formatted_key)
            
            if success:
                print(f"  → {key}")
            
            # Apply delay based on key type
            if delay is not None:
                time.sleep(delay)
            elif key == "Right":
                time.sleep(1)  # Expansion needs more time
            elif key in ["Up", "Down"]:
                time.sleep(0.1)  # Sibling navigation
            elif key == "Left":
                time.sleep(0.3)  # Collapse needs moderate time
            
            return success
        except Exception as e:
            print(f"❌ Error sending key '{key}': {e}")
            return False
    
    def navigate_to_path(self, target_path: str) -> bool:
        """
        Navigate to target path using TreeviewPathComputer.
        
        Args:
            target_path: Dot notation path (e.g., "1.2", "2.1", "3")
            
        Returns:
            True if navigation successful, False otherwise
        """
        if not self.automation:
            print("❌ Not connected to any window")
            return False
        
        if not target_path or target_path.strip() == "":
            return False
        
        # If we're already at the target, do nothing
        if self.current_path == target_path:
            print(f"✅ Already at {target_path}")
            return True
        
        try:
            print(f"🎯 Navigating from {self.current_path} to {target_path}")
            
            # Get key sequence from path computer
            key_sequence = self.path_computer.compute_navigation_path(self.current_path, target_path)
            
            if not key_sequence:
                print("✅ No navigation needed")
                return True
            
            print(f"📝 Key sequence: {key_sequence}")
            
            # Allow window to properly gain focus
            time.sleep(0.3)
            
            # Execute key sequence, handling collapse_count for Left keys
            for i, key in enumerate(key_sequence):
                # For the very first key press, use UI change detection
                if self.first_navigation and i == 0:
                    print(f"🎯 First navigation - using UI change detection for '{key}'")
                    if key == "Left":
                        # Send multiple left arrows if needed for collapse
                        for j in range(self.collapse_count):
                            if j == 0:
                                # Use UI change detection for the first left arrow
                                if not self.automation.send_key_with_ui_wait("{Left}"):
                                    return False
                            else:
                                if not self.send_key("Left"):
                                    return False
                            # Small delay between multiple left arrows
                            if j < self.collapse_count - 1:
                                time.sleep(0.2)
                    else:
                        # Map key to proper format for automation helper
                        formatted_key = f"{{{key}}}"
                        if not self.automation.send_key_with_ui_wait(formatted_key):
                            return False
                    self.first_navigation = False  # Reset flag after first key
                else:
                    # Regular key handling for subsequent keys
                    if key == "Left":
                        # Send multiple left arrows if needed for collapse
                        for j in range(self.collapse_count):
                            if not self.send_key("Left"):
                                return False
                            # Small delay between multiple left arrows
                            if j < self.collapse_count - 1:
                                time.sleep(0.2)
                    else:
                        if not self.send_key(key):
                            return False
            
            # Update current path on success
            self.current_path = target_path
            print(f"✅ Successfully navigated to {target_path}")
            return True
                
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
def main():
    """Simple console interface for TreeView Navigator."""
    navigator = TreeViewNavigator(window_title="New Template", collapse_count=2)
    
    print("🌳 TreeView Navigator")
    print("=" * 30)
    
    test_paths = ["1.1.1", "1.1.2", "1.3.1"]
    
    for path in test_paths:
        print(f"\nNavigating to {path}")
        time.sleep(3)  # Give time to observe
        navigator.navigate_to_path(path)


if __name__ == "__main__":
    main()
