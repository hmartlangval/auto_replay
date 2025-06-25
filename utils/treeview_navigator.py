"""
TreeView Navigator - Console interface for navigating real UI treeviews
using smart expand/collapse navigation with keyboard automation.
"""

import time
from typing import List, Optional
from windows_automation import ManualAutomationHelper


class TreeViewNavigator:
    """
    Smart tree navigator that sends keyboard keys to real UI treeview controls.
    Uses collapse-reset-expand strategy for reliable cross-parent navigation.
    """
    
    def __init__(self, window_title: str = None):
        """
        Initialize the navigator for a specific window containing a treeview.
        
        Args:
            window_title: Title of the window containing the treeview
        """
        self.automation = None
        self.current_path = "root"
        self.navigation_steps = []
        self.key_delay = 0.1  # Delay between key presses
        
        if window_title:
            self.connect_to_window(window_title)
    
    def connect_to_window(self, window_title: str) -> bool:
        """Connect to a window containing a treeview."""
        try:
            self.automation = ManualAutomationHelper(target_window_title=window_title)
            print(f"✅ Connected to window: {self.automation.target_window_title}")
            self.current_path = "root"
            self.navigation_steps.clear()
            return True
        except Exception as e:
            print(f"❌ Error connecting to window: {e}")
            return False
    
    def send_key(self, key: str, description: str = "") -> bool:
        """
        Send a key to the target window.
        
        Args:
            key: Key to send (e.g., "{Up}", "{Down}", "{Left}", "{Right}")
            description: Optional description for logging
            
        Returns:
            True if successful, False otherwise
        """
        if not self.automation:
            print("❌ Not connected to any window")
            return False
        
        try:
            success = self.automation.keys(key)
            if success and description:
                self.navigation_steps.append(description)
                print(f"  → {description}")
            time.sleep(self.key_delay)
            return success
        except Exception as e:
            print(f"❌ Error sending key '{key}': {e}")
            return False
    
    def navigate_right(self) -> bool:
        """Send right arrow key (expand or move to first child)."""
        return self.send_key("{Right}", "Right arrow (expand/enter)")
    
    def navigate_left(self) -> bool:
        """Send left arrow key (collapse or move to parent)."""
        return self.send_key("{Left}", "Left arrow (collapse/exit)")
    
    def navigate_up(self) -> bool:
        """Send up arrow key (move to previous sibling)."""
        return self.send_key("{Up}", "Up arrow (previous sibling)")
    
    def navigate_down(self) -> bool:
        """Send down arrow key (move to next sibling)."""
        return self.send_key("{Down}", "Down arrow (next sibling)")
    
    def are_siblings(self, path1: str, path2: str) -> bool:
        """Check if two paths represent siblings (same parent)."""
        if not path1 or not path2 or path1 == "root" or path2 == "root":
            return False
        
        parts1 = path1.split('.')
        parts2 = path2.split('.')
        
        # Same parent if all parts except last are identical
        return parts1[:-1] == parts2[:-1]
    
    def navigate_to_path(self, target_path: str) -> bool:
        """
        Smart navigation to target path using the collapse-reset-expand strategy.
        
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
        
        # Handle root navigation
        if target_path.lower() == "root":
            return self._navigate_to_root()
        
        # If we're already at the target, do nothing
        if self.current_path == target_path:
            print(f"✅ Already at {target_path}")
            return True
        
        try:
            # Parse target indices
            target_indices = [int(x) for x in target_path.split('.')]
            
            print(f"\n🎯 Navigating from {self.current_path} to {target_path}")
            self.navigation_steps.clear()
            
            # Check if it's sibling navigation or cross-parent navigation
            if self.current_path != "root" and self.are_siblings(self.current_path, target_path):
                success = self._navigate_within_siblings(target_path)
            else:
                success = self._navigate_cross_parent(target_path)
            
            if success:
                self.current_path = target_path
                print(f"✅ Successfully navigated to {target_path}")
            else:
                print(f"❌ Failed to navigate to {target_path}")
            
            return success
                
        except ValueError:
            print(f"❌ Invalid path format: {target_path}")
            return False
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    def _navigate_within_siblings(self, target_path: str) -> bool:
        """Navigate within same parent using simple up/down arrows."""
        print("📍 Sibling navigation - using up/down arrows")
        
        target_indices = [int(x) for x in target_path.split('.')]
        current_indices = [int(x) for x in self.current_path.split('.')]
        
        # Calculate how many steps up or down
        current_pos = current_indices[-1]
        target_pos = target_indices[-1]
        steps = target_pos - current_pos
        
        # Move up or down
        if steps > 0:
            for i in range(steps):
                if not self.navigate_down():
                    return False
        elif steps < 0:
            for i in range(abs(steps)):
                if not self.navigate_up():
                    return False
        
        return True
    
    def _navigate_cross_parent(self, target_path: str) -> bool:
        """
        Navigate across different parents using collapse-reset-expand strategy.
        1. Collapse current branch and move to parent level (root)
        2. Navigate to target parent
        3. Expand target parent and navigate to target child
        """
        print("🔄 Cross-parent navigation - using collapse-reset-expand strategy")
        
        # Step 1: Collapse current branch and move to root level
        print("  Step 1: Collapsing to root level")
        if not self._navigate_to_root():
            return False
        
        # Step 2: Navigate to target
        target_indices = [int(x) for x in target_path.split('.')]
        
        # Expand root to see children (if not already)
        print("  Step 2: Expanding root")
        if not self.navigate_right():
            return False
        
        # Navigate to each level
        for level, target_index in enumerate(target_indices):
            if level > 0:
                # Expand current node to see children
                print(f"  Step {level + 2}: Expanding level {level}")
                if not self.navigate_right():
                    return False
            
            # Navigate to correct position at this level
            current_pos = 1  # Start at position 1
            while current_pos != target_index:
                if current_pos < target_index:
                    if not self.navigate_down():
                        return False
                    current_pos += 1
                else:
                    if not self.navigate_up():
                        return False
                    current_pos -= 1
        
        return True
    
    def _navigate_to_root(self) -> bool:
        """Navigate back to root by pressing left arrow exactly the right number of times."""
        if self.current_path == "root":
            return True
        
        print("  🏠 Navigating to root")
        
        # Calculate exact number of left arrows needed based on current path depth
        path_parts = self.current_path.split('.')
        depth = len(path_parts)
        
        print(f"  Current depth: {depth}, need {depth} left arrows")
        
        # Press left arrow exactly 'depth' times
        for i in range(depth):
            if not self.navigate_left():
                print(f"❌ Failed at left arrow {i+1}/{depth}")
                return False
        
        self.current_path = "root"
        return True
    
    def list_windows(self) -> List[tuple]:
        """List all available windows for manual selection."""
        from utils.windows_automation import list_all_windows
        
        windows = list_all_windows()
        if not windows:
            print("No windows found")
            return []
        
        print("\nAvailable windows:")
        print("-" * 60)
        for i, (hwnd, title) in enumerate(windows, 1):
            print(f"{i:3d}. {title}")
        
        return windows
    
    def set_key_delay(self, delay: float):
        """Set delay between key presses (in seconds)."""
        self.key_delay = max(0.05, delay)  # Minimum 50ms delay
        print(f"Key delay set to {self.key_delay}s")
    
    def show_status(self):
        """Show current navigation status."""
        if not self.automation:
            print("❌ Not connected to any window")
            return
        
        print(f"\n📍 Current Status:")
        print(f"  Window: {self.automation.target_window_title}")
        print(f"  Current Path: {self.current_path}")
        print(f"  Key Delay: {self.key_delay}s")
        
        if self.navigation_steps:
            print("  Recent Steps:")
            for step in self.navigation_steps[-5:]:  # Show last 5 steps
                print(f"    - {step}")


def main():
    """Simple console interface for TreeView Navigator."""
    navigator = TreeViewNavigator(window_title="New Template")
    
    print("🌳 TreeView Navigator")
    print("=" * 30)
    
    # Initial window connection
    # window_title = input("Enter window title to connect: ").strip()
    # if not window_title or not navigator.connect_to_window(window_title):
    #     print("❌ Failed to connect. Exiting.")
    #     return
    
    print(f"Current position: {navigator.current_path}")
    print()
    
    # Simple navigation loop
    while True:
        try:
            target = input("Where do you want to navigate next? ").strip()
            
            if not target or target.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            navigator.navigate_to_path(target)
            print(f"Current position: {navigator.current_path}")
            print()
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
