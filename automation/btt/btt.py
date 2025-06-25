# Brand Test Tool Automation
# Uses all existing functions from utils - no reinventing functionality

import sys
import os
import time

from utils.windows_automation import find_windows_by_title_starts_with
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils import (
    find_windows_by_title, get_window_info, ManualAutomationHelper, NavigationParser, setup_window_by_handle
)


class BrandTestToolAutomation:
    """Automation class for Brand Test Tool with modular step control"""
    
    def __init__(self):
        self.window_title = "Brand Test Tool"
        
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
        if not self.send_navigation_keys(navigation_path="{Alt+C} -> {Down 1} -> {Enter}"):
            return False
        
        time.sleep(1)
        
        # Search for a new window
        project_setup_window = find_windows_by_title_starts_with("Project Settings -")
        print(f"✅ Found Project Setup window: {project_setup_window}")
        if not project_setup_window:
            print("❌ No Project Setup window found")
            return False
        
        setup_window_by_handle(project_setup_window[0][0], (100, 100, 1050, 646))
        
        # Click on the window
        if not self.automation_helper.click(project_setup_window[0][0]):
            return False
        
        time.sleep(1)
        
        
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
    btt_automation = BrandTestToolAutomation()
    
    # Option 1: Execute all steps at once
    btt_automation.execute_all_steps()
    
    # Option 2: Execute functions individually for full control
    # btt_automation.send_navigation_keys()
    
    # Option 3: Custom navigation path
    # btt_automation.send_navigation_keys("{Ctrl+N} -> {Tab 3} -> {Enter}")