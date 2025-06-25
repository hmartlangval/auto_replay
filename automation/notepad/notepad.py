# Notepad Automation
# Uses all existing functions from utils - no reinventing functionality

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils import (
   ManualAutomationHelper, NavigationParser
)


class NotepadAutomation:
    """Automation class for Notepad with modular step control"""
    
    def __init__(self):
        self.window_title = "Untitled - Notepad"
        
        # Initialize automation helper with the found window handle
        self.automation_helper = ManualAutomationHelper(target_window_title=self.window_title)
        self.window_handle = self.automation_helper.hwnd
        self.window_info = self.automation_helper.get_window_info()
   
    def send_navigation_keys(self, navigation_path="{Alt+F} -> {Down 1} -> {Enter}"):
        """Send navigation keys using the navigation parser"""
        try:
            print(f"⌨️ Step 3: Sending navigation keys: '{navigation_path}'...")
            
            if not self.automation_helper:
                print("❌ No automation helper available. Run bring_to_focus() first.")
                return False
            
            # Parse the navigation path
            steps = NavigationParser.parse_navigation_path(navigation_path)
            
            if not steps:
                print("❌ Failed to parse navigation path")
                return False
            
            print(f"📝 Parsed {len(steps)} navigation steps")
            
            # Execute each step using Windows API
            for i, step in enumerate(steps, 1):
                print(f"  Step {i}/{len(steps)}: {step['description']}")
                success = NavigationParser.execute_step_windows(step, self.automation_helper)
                if not success:
                    print(f"❌ Failed to execute step {i}")
                    return False
                time.sleep(0.2)  # Small delay between steps
            
            print("✅ All navigation steps executed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Step 3 failed: {e}")
            return False
    
    def execute_all_steps(self):
        """Execute all steps in sequence"""
        print(f"🚀 Starting {self.window_title} automation...")
        
        if not self.window_handle:
            return False
     
        # Send navigation keys
        if not self.send_navigation_keys(navigation_path="{Alt+F} -> {Down 1} -> {Enter}"):
            return False
        
        new_window_automation_helper = ManualAutomationHelper(target_window_title="Untitled - Notepad")
        print(f"✅ Found window: {new_window_automation_helper.target_window_title}.")
        
        # Type text
        if not new_window_automation_helper.type("Hello, world!"):
            print("❌ Failed to type text")
            return False
        
        print("🎉 All automation steps completed successfully!")
        return True
    
    def get_window_info(self):
        """Get current window information"""
        return self.window_info
    
    def get_automation_helper(self):
        """Get the automation helper instance"""
        return self.automation_helper
    
    def reset(self):
        """Reset the automation state"""
        self.automation_helper = None
        self.window_handle = None
        self.window_info = None
        print("🔄 Automation state reset")


# Example usage
if __name__ == "__main__":
    # Create automation instance
    notepad_automation = NotepadAutomation()
    
    # Option 1: Execute all steps at once
    notepad_automation.execute_all_steps()
    
    # Option 2: Execute functions individually for full control
    # notepad_automation.search_window()
    # notepad_automation.bring_to_focus()
    # notepad_automation.send_navigation_keys()
    
    # Option 3: Custom navigation path
    # notepad_automation.send_navigation_keys("{Ctrl+N} -> {Tab 3} -> {Enter}")