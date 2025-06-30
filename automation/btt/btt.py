# Brand Test Tool Automation
# Uses all existing functions from utils - no reinventing functionality

import sys
import os
import time
import traceback
import functools

# Add parent directory to path first
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils import (
    ManualAutomationHelper, NavigationParser, play_sequence, play_sequence_async
)
from utils.treeview.treeview_navigator import TreeViewNavigator
from utils.image_scanner import scan_for_all_occurrences, scan_for_image
from utils.graphics import ScreenOverlay, visualize_image_search
from helpers import select_countries, start_questionnaire
from questionnaire_filler import QuestionnaireFiller
from forms import DefaultQuestionnaireForms, CustomQuestionnaireForms

from dotenv import load_dotenv
load_dotenv()
LOCAL_DEV = os.getenv("LOCAL_DEV", "False") == "True"
DEBUG_VISUALIZATION = True

def critical_exception_handler(func):
    """
    Global decorator for critical exception handling with automatic process termination.
    
    PURPOSE:
    - Prevents BTT automation from hanging when critical exceptions occur
    - Eliminates need for user to manually press Ctrl+C to terminate hung processes
    - Provides comprehensive error logging for debugging failed automation runs
    - Ensures clean process termination using existing shutdown mechanisms
    
    WHY THIS APPROACH:
    - BTT runs as subprocess launched from GUI - hanging processes are problematic
    - User should not need to intervene when automation fails critically
    - Catching at decorator level ensures ALL critical functions are protected
    - Using sys.exit(1) leverages existing shutdown logic (no reinventing the wheel)
    - Comprehensive logging helps debug automation failures
    
    USAGE:
    - Apply @critical_exception_handler to any function that could fail critically
    - Already applied to: execute_all_steps(), fill_questionnaire(), main()
    - Any uncaught exception in wrapped functions triggers automatic shutdown
    
    TECHNICAL FLOW:
    1. Function executes normally if no exceptions
    2. Any exception caught → detailed logging → sys.exit(1) 
    3. Parent GUI process detects subprocess death via monitoring
    4. GUI button resets from "Stop BTT" back to "BTT"
    
    FUTURE MAINTENANCE:
    - Add this decorator to any new critical BTT functions
    - If you see hanging BTT processes, check if functions are wrapped
    - Modify logging format here if you need different error details
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"\n💥 CRITICAL EXCEPTION OCCURRED in {func.__name__}:")
            print(f"❌ Error: {str(e)}")
            print(f"📍 Exception Type: {type(e).__name__}")
            print("\n🔍 Full Traceback:")
            traceback.print_exc()
            print(f"\n🛑 INITIATING ULTIMATE SHUTDOWN - Process will terminate automatically...")
            print("=" * 60)
            
            # Use existing ultimate shutdown mechanism - don't reinvent the wheel
            sys.exit(1)
            
    return wrapper

class BrandTestToolAutomation:
    """Automation class for Brand Test Tool with modular step control"""
    
    def __init__(self):
        self.window_title = "Brand Test Tool"
        
        # Initialize automation helper with the found window handle
        self.automation_helper = ManualAutomationHelper(target_window_title=self.window_title)
        self.window_handle = self.automation_helper.hwnd
        self.window_info = self.automation_helper.get_window_info()
        self.graphics = ScreenOverlay()

    def _show_debug_visualization(self, search_region, found_locations=None, target_location=None, duration=3):
        """Show clean debug visualization using a temporary transparent window"""
        if not DEBUG_VISUALIZATION:
            return
            
        import tkinter as tk
        import threading
        import time as time_module
        
        def create_and_show():
            # Create a temporary transparent window
            root = tk.Tk()
            root.withdraw()  # Hide initially
            
            # Make it fullscreen and completely transparent
            root.attributes('-fullscreen', True)
            root.attributes('-topmost', True)
            root.attributes('-alpha', 1.0)  # Fully opaque for the shapes
            root.overrideredirect(True)
            
            # Make the window background transparent
            try:
                root.wm_attributes('-transparentcolor', 'black')
            except:
                pass
            
            # Create transparent canvas with black background (which becomes transparent)
            canvas = tk.Canvas(root, bg='black', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Draw search region rectangle (green)
            canvas.create_rectangle(
                search_region[0], search_region[1], search_region[2], search_region[3],
                outline='#00FF00', width=3, fill=''
            )
            
            # Draw found locations (red circles)
            if found_locations:
                for x, y in found_locations:
                    canvas.create_oval(
                        x-15, y-15, x+15, y+15,
                        outline='#FF0000', width=3, fill=''
                    )
            
            # Draw target location (yellow circle, larger)
            if target_location:
                x, y = target_location
                canvas.create_oval(
                    x-25, y-25, x+25, y+25,
                    outline='#FFFF00', width=5, fill=''
                )
            
            # Show the window
            root.deiconify()
            root.update()
            
            # Auto-hide after duration
            def cleanup():
                time_module.sleep(duration)
                try:
                    root.destroy()
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
            # Start the window's event loop in this thread
            try:
                root.mainloop()
            except:
                pass
        
        # Run in separate thread to avoid blocking
        threading.Thread(target=create_and_show, daemon=True).start()

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
        
        max_iterations = 3  # Maximum consecutive failed attempts
        iteration = 0
        
        while iteration < max_iterations:
            print(f"\n🔄 Iteration {iteration + 1}: Searching for expanded tree items...")
            
            # Visual debug: Show search region
            if DEBUG_VISUALIZATION:
                print(f"🔍 Search region: {search_region}")
                self._show_debug_visualization(search_region, duration=2)
            
            # Search for all minus-expanded.png images in the search region
            results = scan_for_all_occurrences(
                image_name="minus-expanded.png",
                bounding_box=search_region,
                threshold=0.8
            )
            
            if not results or len(results) == 0:
                iteration += 1  # Increment counter for failed attempt
                print(f"❌ No expanded tree items found. Failed attempt {iteration}/{max_iterations}")
                # Visual debug: Show final search region with no matches
                if DEBUG_VISUALIZATION:
                    print("🎯 No expanded items found in this iteration")
                    self._show_debug_visualization(search_region, duration=2)
                
                if iteration >= max_iterations:
                    print("✅ No more expanded tree items found after 3 consecutive attempts. Collapse complete!")
                    break
                continue
            
            print(f"📍 Found {len(results)} expanded tree items")
            iteration = 0  # Reset counter when matches are found
            
            # Visual debug: Show complete visualization with all elements
            if DEBUG_VISUALIZATION:
                print(f"🎯 Found locations: {results}")
                sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                print(f"🎯 Will click bottommost at: {sorted_results[0] if sorted_results else 'None'}")
                
                target_location = sorted_results[0] if sorted_results else None
                self._show_debug_visualization(
                    search_region=search_region,
                    found_locations=results,
                    target_location=target_location,
                    duration=3
                )
            
            # Sort results by Y coordinate (bottom to top)
            # results format: [(x, y), ...]
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
            
            # Click the bottommost expanded item
            center_x, center_y = sorted_results[0]
            print(f"🖱️  Clicking bottommost expanded item at ({center_x}, {center_y})")
            
            # Ensure window is focused and try multiple click approaches
            automation_helper._bring_to_focus()
            time.sleep(0.2)
            
            # Try direct click first
            success = automation_helper.click((center_x, center_y))
            
            # If that fails, try a more aggressive approach
            if not success:
                print(f"⚠️  Direct click failed, trying alternative methods...")
                # Try moving mouse first, then clicking
                automation_helper.move_mouse(center_x, center_y)
                time.sleep(0.1)
                success = automation_helper.click((center_x, center_y))
            
            if not success:
                print(f"❌ All click methods failed at ({center_x}, {center_y})")
                break
            
            # Wait for the UI to update
            time.sleep(0.5)
        
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
    
    @critical_exception_handler
    def fill_questionnaire(self, edit_window, forms_class=None):
        """
        Fill the questionnaire using the QuestionnaireFiller class
        
        Args:
            edit_window: The window to perform automation on
            forms_class: Optional forms class to use. If None, uses DefaultQuestionnaireForms
        """
        
        # Initialize the questionnaire filler with specified forms class
        qf = QuestionnaireFiller(edit_window, forms_class=forms_class)
        forms = qf.questionnaire_forms
        
        # Start filling questionnaires
        
        # Step 1: Select countries
        if not forms.country(["United States"]):
            return False
        
        # Step 2: Processor name
        if not forms.processor_name("Fiserv"):
            return False
        
        # Step 3: User/tester information
        if not forms.user_tester_information("Tester", "Tester@thoughtfocus.com"):
            return False
        
        # Step 4: Testing details
        if not forms.testing_details(check_first=True, check_second=True):
            return False
        
        # Step 5: Deployment type
        if not forms.deployment_type(dropdown_down_count=1):
            return False
        
        # Step 6: Merchant information
        if not forms.merchant_information():
            return False
        
        # Step 7: Terminal ATM information
        if not forms.terminal_atm_information("terminal name", "model name", "version info"):
            return False
       
        # Step 8: Contactless ATM information
        if not forms.contactless_atm_information("ATM1", "ATM2"):
            return False
        
        # Step 9: Contact chip ODA
        if not forms.contact_chip_oda(select_first=True, select_second=True):
            return False
        
        # Step 10: Contact only features
        if not forms.contact_only_features(select_first_set=True, select_second_set=True):
            return False
        
        # Step 11: Comment box
        if not forms.comment_box("some comment"):
            return False
        
        # Step 12: Confirm final information
        if not forms.confirm_final_information():
            return False
        
        # Step 13: Test session name
        if not forms.test_session_name("some test session name"):
            return False
        
        # Final step - with all successful, we have a screen where OK button is auto highlighted
        time.sleep(3)
        edit_window.keys("{space}")
        
        print("🎉 All automation steps completed successfully!")
        print('Task completed. Exiting...')
        exit()
    
    @critical_exception_handler
    def fill_questionnaire_v2(self, questionnaire_window, forms_class=None):
        # Initialize the questionnaire filler with specified forms class
        
        # Steps:
        execution_steps = """
            # File-based execution steps
            country: [United States (US)]
            processor_name: File-based Processor
            user_tester_information: File Tester, file@test.com
            testing_details: true, true
            deployment_type: 1
            terminal_implementation: true
            visa_products_accepted: true, true, true
            merchant_information:
            terminal_atm_information: Ingenico, DESK/5000, Test application V1
            reference_number: 13050 0514 400 21 CET,2-04683-3-8C-FIME-1020-4.3i,15911 1117 260 26b 26b CETI,CDINGE01916
            contact_chip_oda: true
            contact_chip_cvm: true, true, true, false, false, true
            contact_only_features: false, true, true
            contactless_chip_cvms: true, true, true, false
            contactless_only_features: false
            pin_opt_out_mechanism: 1, 1
            fleet_2_0: false
            comment_box:
            confirm_final_information:
            sleep: 2
            apply_ok:
            """
        
        qf = QuestionnaireFiller(questionnaire_window, forms_class=forms_class)
        forms = qf.questionnaire_forms
        print("🚀 Execution using steps loaded from custom defined steps:")
        result = qf.execute(execution_steps)
        
        if result:
            print("✅ File-based approach completed successfully\n")
        else:
            print("❌ File-based approach failed\n")
    
    @critical_exception_handler
    def execute_all_steps(self):
        """Execute all steps in sequence"""
        print(f"🚀 Starting {self.window_title} automation...")
        
        if not self.window_handle:
            return False
     
        if not self.create_new_project():
            return False
       
        time.sleep(1)
        
        if not (project_setup_window_handle := self.prepare_project_setup_window()):
            return False
        
        # # Now we are ready to navigate to the node we want to edit
        navigator = TreeViewNavigator(automation_helper=project_setup_window_handle, collapse_count=2)
        
        # # retrieve data from pre-processed data where to navigate, assume 1.7.2
        # # and then put a check on the current node by pressing space key 
        time.sleep(1.5)
        navigator.navigate_to_path("1.7.2")
        time.sleep(0.2)
        project_setup_window_handle.keys("{space}")
        time.sleep(1) # gives time for the right panel to get populated
        
        # click on start test
        questionnaire_window = start_questionnaire(project_setup_window_handle, questionnaire_window_title="Edit EMVCo L3 Test Session - Questionnaire")
        if not questionnaire_window:
            print("❌ No questionnaire window found")
            return False
        
        time.sleep(1)
        
        # Option 1: Use default forms with manual method calls
        self.fill_questionnaire_v2(questionnaire_window)
        
        # Option 2: Use declarative execution (uncomment to use)
        # qf = QuestionnaireFiller(project_setup_window_handle)
        # qf.execute()  # Uses default execution steps
        
        # Option 3: Use custom forms with declarative execution (uncomment to use)
        # qf_custom = QuestionnaireFiller(project_setup_window_handle, forms_class=CustomQuestionnaireForms)
        # qf_custom.execute()  # Uses custom execution steps
        # ewindow = ManualAutomationHelper(target_window_title="Edit EMVCo L3 Test Session - Questionnaire", title_starts_with=True)
        # time.sleep(1)
        # self.send_tabs(ewindow, 2)
        # if not select_countries(ewindow, ["Algeria"]):
        #     print("❌ Failed to select countries")
        #     return False
        
        # self.send_tabs(ewindow, 2, followed_by_space=True)
        
        # # acquire processor name
        # # this one has a single text input
        # time.sleep(1)
        # self.send_tabs(ewindow, 2)
        # ewindow.type("some duummy name")
        # # ewindow.keys("{tab}")
        # # time.sleep(0.5)
        # # ewindow.keys("{space}")
        # self.send_tabs(ewindow, 1, followed_by_space=True)
        
        # self.fill_questionnaire(pswindow)
        return True
    
    def send_tabs(self, automation_helper, count, followed_by_space=False, followed_by_enter=False, start_delay=0.01, end_delay=0.01):
        time.sleep(start_delay)
        for _ in range(count):
            time.sleep(0.2)
            automation_helper.keys("{tab}")
            
        time.sleep(end_delay)
            
        if followed_by_space:
            time.sleep(0.2)
            automation_helper.keys("{space}")
            
        if followed_by_enter:
            time.sleep(0.2)
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


# CUSTOM_MODE = "START_FROM_CLICK_START_TEST"
CUSTOM_MODE = "START_FROM_CUSTOM"

@critical_exception_handler
def main():
    """Main execution function with critical exception handling"""
    # Create automation instance
    btt_automation = BrandTestToolAutomation()
    
    if CUSTOM_MODE and CUSTOM_MODE != "":
        if not (pwin := ManualAutomationHelper(target_window_title="Project Settings", title_starts_with=True)):
            print("❌ No project settings window found")
            exit()
        
        if CUSTOM_MODE == "START_FROM_CUSTOM":
            if not (edit_window := ManualAutomationHelper(target_window_title="Edit EMVCo L3 Test Session - Questionnaire")):
                print("❌ No edit window found")
                exit()
            qf = QuestionnaireFiller(edit_window)
            qf.questionnaire_forms.values["testing_contact"] = True
            qf.questionnaire_forms.values["testing_contactless"] = True
            qf.execute("""
                    # country: [United States (US)]
                    # processor_name: File-based Processor
                    # user_tester_information: File Tester, file@test.com
                    # testing_details: true, true
                    # deployment_type: 1
                    # terminal_implementation: true
                    # visa_products_accepted: true, true, true
                    # merchant_information:
                    # terminal_atm_information: Ingenico, DESK/5000, Test application V1
                    # reference_number: 13050 0514 400 21 CET,2-04683-3-8C-FIME-1020-4.3i,15911 1117 260 26b 26b CETI,CDINGE01916
                    contact_chip_oda: true
                    contact_chip_cvm: true, true, true, false, false, true
                    contact_only_features: false, true, true
                    contactless_chip_cvms: true, true, true, false
                    contactless_only_features: false
                    pin_opt_out_mechanism: 1, 1
                    fleet_2_0: false
                    comment_box:
                    confirm_final_information:
                    sleep: 2
                    apply_ok:
                    """)
        elif CUSTOM_MODE == "START_FROM_CLICK_START_TEST":
            if not (edit_window := start_questionnaire(pwin, questionnaire_window_title="Edit EMVCo L3 Test Session - Questionnaire")):
                print("❌ No edit window found")
                exit()
            qf = QuestionnaireFiller(edit_window)
            btt_automation.fill_questionnaire_v2(edit_window)
            
        print("Custom Mode Execution completed.")
        exit(0)
    
    # # Option 1: Use default forms
    # btt_automation.fill_questionnaire(edit_window)
    
    # Option 2: Use custom forms (uncomment to use)
    # btt_automation.fill_questionnaire(edit_window, forms_class=CustomQuestionnaireForms)
    
    # Option 1: Execute all steps at once
    btt_automation.execute_all_steps()
    
    # Option 2: Execute functions individually for full control
    # btt_automation.send_navigation_keys()
    
    # Option 3: Custom navigation path
    # btt_automation.send_navigation_keys("{Ctrl+N} -> {Tab 3} -> {Enter}")

# Example usage
if __name__ == "__main__":
    main()