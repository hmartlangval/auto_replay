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
from utils.treeview.treeview_navigator import TreeViewNavigator
from utils.image_scanner import scan_for_all_occurrences, scan_for_image
from utils.graphics import ScreenOverlay, visualize_image_search
from helpers import select_countries, start_questionnaire

from dotenv import load_dotenv
load_dotenv()
LOCAL_DEV = os.getenv("LOCAL_DEV", "False") == "True"
DEBUG_VISUALIZATION = True

class BrandTestToolAutomation:
    """Automation class for Brand Test Tool with modular step control"""
    
    def __init__(self):
        self.window_title = "Brand Test Tool"
        
        # Initialize automation helper with the found window handle
        self.automation_helper = ManualAutomationHelper(target_window_title=self.window_title)
        self.window_handle = self.automation_helper.hwnd
        self.window_info = self.automation_helper.get_window_info()
        self.graphics = ScreenOverlay()
   
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
    
    def create_new_project(self):
        """Create a new project"""
        print("🚀 Starting {self.window_title} automation...")
        
        # Send navigation keys to create project
        if not self.send_navigation_keys(navigation_path="{Alt+F} -> {Down 1} -> {Enter}"):
            return False
        
        time.sleep(0.5)
        
        # Run sequence to fill in project name and description
        print("🎬 Running sequence to fill project details...")
        success = play_sequence("fill_project_details", blocking=True)
        if not success:
            print("❌ Failed to run sequence")
            return False
        
        return True
    def collapse_tree_items(self,automation_helper=None):
        """
        Collapse all tree items by clicking minus-expanded.png images from bottom to top.
        Searches only in the top-left 30% of the window's bounding box.
        """
        
        if automation_helper is None and not LOCAL_DEV:
            raise ValueError("automation_helper is required when not in local development mode")
        
        # Get the window's bounding box
        if LOCAL_DEV:
            bbox = (100, 100, 1050, 646)
        else:
            bbox = automation_helper.get_bbox()
        left, top, right, bottom = bbox
        
        # Calculate the top-left 30% region
        search_width = int((right - left) * 0.3)  # 30% of width
        search_height = int((bottom - top) * 0.5)  # 50% of height
        search_region = (left, top, left + search_width, top + search_height)
        
        print(f"📐 Window bbox: {bbox}")
        print(f"🔍 Search region (top-left 30%): {search_region}")
        
        self.graphics.draw_rectangle(search_region[0], search_region[1], search_region[2], search_region[3], color="#00FF00", width=3, label="Search Region")
        
        max_iterations = 20  # Safety limit to prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}: Searching for expanded tree items...")
            
            # Visualize the search region (only if debug enabled)
            visualize_image_search(
                search_region=search_region,
                region_label=f"Tree Search Region (Iteration {iteration})",
                show_duration=2.0,
                enabled=DEBUG_VISUALIZATION
            )
            
            # Search for all minus-expanded.png images in the search region
            results = scan_for_all_occurrences(
                image_name="minus-expanded.png",
                bounding_box=search_region,
                threshold=0.8
            )
            
            if not results or len(results) == 0:
                print("✅ No more expanded tree items found. Collapse complete!")
                # Show final visualization with no matches
                visualize_image_search(
                    search_region=search_region,
                    found_locations=[],
                    region_label="Final Search - No Matches",
                    show_duration=3.0,
                    enabled=DEBUG_VISUALIZATION
                )
                break
            
            print(f"📍 Found {len(results)} expanded tree items")
            
            # Show visualization with found locations
            visualize_image_search(
                search_region=search_region,
                found_locations=results,
                region_label=f"Found {len(results)} Tree Items",
                show_duration=3.0,
                enabled=DEBUG_VISUALIZATION
            )
            
            # Sort results by Y coordinate (bottom to top)
            # results format: [(x, y), ...]
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
            
            # Click the bottommost expanded item
            center_x, center_y = sorted_results[0]
            print(f"🖱️  Clicking bottommost expanded item at ({center_x}, {center_y})")
            
            # Click the minus icon to collapse
            success = automation_helper.click((center_x, center_y))
            if not success:
                print(f"❌ Failed to click at ({center_x}, {center_y})")
                break
            
            # Wait for the UI to update
            time.sleep(0.5)
            
            # Optional: Verify the click worked by checking if the item is still there
            # This helps ensure we're making progress
            verification_results = scan_for_all_occurrences(
                image_name="minus-expanded.png",
                bounding_box=search_region,
                threshold=0.8
            )
            
            if verification_results and len(verification_results) >= len(results):
                print("⚠️  Warning: No change detected after click, continuing anyway...")
            else:
                print(f"✅ Progress made: {len(results)} → {len(verification_results) if verification_results else 0} expanded items")
        
        if iteration >= max_iterations:
            print(f"⚠️  Reached maximum iterations ({max_iterations}). Stopping to prevent infinite loop.")
        
        print("🎉 Tree collapse process completed!")

    def prepare_project_setup_window(self):
        """Identify the project setup window. Then ready the treeview for navigation"""
        # Now the Project Settings Window is open
        # Search for a new window
        project_setup_window_handle = ManualAutomationHelper(target_window_title="Project Settings", title_starts_with=True)
        print(f"✅ Found Project Setup window: {project_setup_window_handle.hwnd}")
        if not project_setup_window_handle.hwnd:
            print("❌ No Project Setup window found")
            return False
        
        # # Reposition the window to the desired location such that we can play sequences as recorded and coordinates will not be messed up
        project_setup_window_handle.setup_window(bbox=(100, 100, 1050, 646))
        
        # GOAL: To collapse all tree items from bottom up, so we are guaranteed how the UI looks like
        # use the image search to search for all image in the setup window handle bounding box, the top left 30% of the bounding box only.
        # any images minus-expanded.png found should be clicked from bottom up one at a time, until none is found.
        bbox = project_setup_window_handle.get_bbox()
        left, top, right, bottom = bbox
        search_width = int((right - left) * 0.3)  # 30% of width
        search_height = int((bottom - top))  # 50% of height
        search_region = (left, top, left + search_width, top + search_height)
        self.collapse_tree_items(project_setup_window_handle)
        # Assume at this point that the tree is fully collapsed to the very first root level
        # and that it is currently getting focussed
        
        
        return project_setup_window_handle
    
    def execute_all_steps(self):
        """Execute all steps in sequence"""
        print(f"🚀 Starting {self.window_title} automation...")
        
        if not self.window_handle:
            return False
     
        # if not self.create_new_project():
        #     return False
       
        # time.sleep(1)
        
        if not (project_setup_window_handle := self.prepare_project_setup_window()):
            return False
        
        # Now we are ready to navigate to the node we want to edit
        navigator = TreeViewNavigator(automation_helper=project_setup_window_handle, collapse_count=2)
        
        # retrieve data from pre-processed data where to navigate, assume 1.7.2
        # and then put a check on the current node by pressing space key 
        navigator.navigate_to_path("1.7.2")
        time.sleep(0.2)
        project_setup_window_handle.keys("{space}")
        time.sleep(1) # gives time for the right panel to get populated
        
        # Start filling questionairres
        if not (edit_emvco_l3_test_session_window := start_questionnaire(project_setup_window_handle, "Edit EMVCo L3 Test Session - Questionnaire")):
            return False
        
        
        # # What we should see now is a tabbed UI and first tab is highlighted
        # # we are looking for a 2nd tab, we ensure we click the right tab by scanning for the unfocussed tab image
        # edit_answers_location = scan_for_image("edit-answers.png", edit_emvco_l3_test_session_window.get_bbox(), threshold=0.8)
        # if edit_answers_location:
        #     edit_emvco_l3_test_session_window.click(edit_answers_location)
        #     time.sleep(2)
        # else:
        #     print("❌ No edit answers button found")
        #     return False
        
        # Start filling questionairres
        
        # selecting countries
        # this one has a multiple select list, space to select, up/down to navigate
        time.sleep(1)
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
    
    def send_tabs(self, automation_helper, count, followed_by_space=False, followed_by_enter=False):
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