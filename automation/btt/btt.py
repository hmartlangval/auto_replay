# Brand Test Tool Automation
# Uses all existing functions from utils - no reinventing functionality

import sys
import os
import time

# Add parent directory to path first
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils import (
    ManualAutomationHelper, NavigationParser, play_sequence, play_sequence_async
)
from utils.image_scanner import scan_for_image
from helpers import select_countries


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
     
        # # Send navigation keys to create project
        # if not self.send_navigation_keys(navigation_path="{Alt+F} -> {Down 1} -> {Enter}"):
        #     return False
        
        # time.sleep(0.5)
        
        # # Run sequence to fill in project name and description
        # print("🎬 Running sequence to fill project details...")
        # success = play_sequence("fill_project_details", blocking=True)
        # if not success:
        #     print("❌ Failed to run sequence")
        #     return False
        
        # time.sleep(1)
        # # Now the Project Settings Window is open
        # # Search for a new window
        # project_setup_window_handle = ManualAutomationHelper(target_window_title="Project Settings", title_starts_with=True)
        # print(f"✅ Found Project Setup window: {project_setup_window_handle.hwnd}")
        # if not project_setup_window_handle.hwnd:
        #     print("❌ No Project Setup window found")
        #     return False
        
        # # Reposition the window to the desired location such that we can play sequences as recorded and coordinates will not be messed up
        # project_setup_window_handle.setup_window(bbox=(100, 100, 1050, 646))
        
        
        # GOAL: To collapse all tree items from bottom up, so we are guaranteed how the UI looks like
        # use the image search to search for all image in the setup window handle bounding box, the top left 30% of the bounding box only.
        # any images minus-expanded.png found should be clicked from bottom up one at a time, until none is found.
        
        
        # GOAL: Expand the first parent node.
        # Now that all of them is collapsed, we know exactly where the tree items are
        # click on the first plus icon "plus-collapsed.png", so the first parent node expanded.
        
        
        # Now that the first parent is expanded, we know exactly the sequence for each child to play
        # we make decisions which sequence to play depending on business logics.
        # each child node has a sequence associated to it, so we implement this later
        
        
        edit_emvco_l3_test_session_window = ManualAutomationHelper(target_window_title="Edit EMVCo L3 Test Session - Questionnaire")
        print(f"✅ Found Project Setup window: {edit_emvco_l3_test_session_window.hwnd}")
        if not edit_emvco_l3_test_session_window.hwnd:
            print("❌ No Project Setup window found")
            return False
        
        
        # Reposition the window to the desired location such that we can play sequences as recorded and coordinates will not be messed up
        # Expected bounding box is BoundingRectangle:	{l:71 t:65 r:1270 b:707}
        edit_emvco_l3_test_session_window.setup_window(bbox=(71, 65, 1270, 707))
        edit_answers_location = scan_for_image("edit-answers.png", edit_emvco_l3_test_session_window.get_bbox(), threshold=0.8)
        if edit_answers_location:
            edit_emvco_l3_test_session_window.click(edit_answers_location)
        else:
            print("❌ No edit answers button found")
            return False
        
        # Start filling questionairres
        
        # selecting countries
        # this one has a multiple select list, space to select, up/down to navigate
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        if not select_countries(edit_emvco_l3_test_session_window, ["Algeria"]):
            print("❌ Failed to select countries")
            return False
        
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_space=True)
        
        # acquire processor name
        # this one has a single text input
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("some duummy name")
        self.send_tabs(edit_emvco_l3_test_session_window, 1)
        
        # acquire processor name
        # this one has a single text input
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("some duummy name")
        self.send_tabs(edit_emvco_l3_test_session_window, 1)
        
        # tester information
        # this one has 2 text inputs, one name and one email
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("uusername")
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("email-test@yopmail.com")
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_space=True)
        
        # testing
        # this one has a checkbox, space to select
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.keys("{space}") # to check the checkbox
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_space=True)
        
        # deployment type
        # this one has a radio input, down arrow to navigate, space to select
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.keys("{down 2}")
        self.send_tabs(edit_emvco_l3_test_session_window, 1, followed_by_space=True)
        
        # terminal ATM/Information
        # this one has 3 text inputs
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("terminal name")
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("model name")
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("version info")
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_enter=True)

        # Reference Number
        time.sleep(1)
        # this one has 2 text inputs
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("reference number")
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("kernel #38293")
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_enter=True)
        
        # Contact chip offline data authentication (ODA)
        # this is a radio input so tab will navigate to different choices, we need to use up/down for toggling the selection
        # for this we ensure we select the first one first, then use arrows if we should change it
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2) 
        edit_emvco_l3_test_session_window.keys("{space}") #selecting the first item
        edit_emvco_l3_test_session_window.keys("{down}") #selecting the second item
        self.send_tabs(edit_emvco_l3_test_session_window, 1, followed_by_space=True)
        
        #Contact Only features
        # another 2 sets of radio inputs
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.keys("{space}") #selecting the first item
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.keys("{space}") #selecting the first item
        self.send_tabs(edit_emvco_l3_test_session_window, 1, followed_by_space=True)
        
        # Comment box
        # this is a single text input
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("some comment")
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_enter=True)
        
        # Test Session Name
        time.sleep(1)
        self.send_tabs(edit_emvco_l3_test_session_window, 2)
        edit_emvco_l3_test_session_window.type("some test session name")
        self.send_tabs(edit_emvco_l3_test_session_window, 2, followed_by_enter=True)
        
        
        # Final information screen
        # This one has a confirm button by default
        time.sleep(1)
        confirm_information_button_location = scan_for_image("confirm-information-button.png", edit_emvco_l3_test_session_window.get_bbox(), threshold=0.8)
        if confirm_information_button_location:
            edit_emvco_l3_test_session_window.click(confirm_information_button_location)
        else:
            print("❌ No confirm information button found")
            return False
        
        time.sleep(3)
        
        # with all successful, we have a screen where OK button is auto highlighted
        # we pressed it
        edit_emvco_l3_test_session_window.keys("{space}")
        
        print("🎉 All automation steps completed successfully!")
        return True
    
    def send_tabs(automation_helper, count, followed_by_space=False, followed_by_enter=False):
        for _ in range(count):
            time.sleep(0.5)
            automation_helper.keys("{tab}")
        if followed_by_space:
            time.sleep(0.5)
            automation_helper.keys("{space}")
        if followed_by_enter:
            time.sleep(0.5)
            automation_helper.keys("{enter}")
    
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