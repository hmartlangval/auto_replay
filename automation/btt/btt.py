# Brand Test Tool Automation
# Uses all existing functions from utils - no reinventing functionality

import sys
import os
import time
import traceback
import functools
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

# Fix Windows console encoding for Unicode emojis in .exe
if sys.platform == 'win32':
    try:
        # Ensure stdout uses UTF-8 encoding to handle Unicode emojis
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Fallback: Set encoding environment variable
        os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add parent directory to path first
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.common import click_apply_ok_button
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

from enum import Enum, auto

class ExecutionMode(Enum):
    """Execution modes for BTT automation"""
    START_FROM_BEGINNING = ""
    START_FROM_QUESTIONNAIRE = "START_FROM_CLICK_START_TEST" 
    START_FROM_CUSTOM = "START_FROM_CUSTOM"
    EXPORT_TEST = "EXPORT_TEST"

class TestType(Enum):
    """Test types supported by BTT automation"""
    VISA = "Visa"
    MASTERCARD = "Mastercard"

class WindowTitle(Enum):
    """Common window titles used in BTT automation"""
    # MAIN_WINDOW = "Untitled - Notepad" # "Brand Test Tool"
    MAIN_WINDOW = "Brand Test Tool"
    PROJECT_SETTINGS = "Project Settings"
    EDIT_QUESTIONNAIRE = "Edit EMVCo L3 Test Session - Questionnaire"

# Set up logging to file
def setup_logging():
    """Set up logging to both console and file"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else '.', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = os.path.join(log_dir, f'btt_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"BTT Automation logging started - Log file: {log_filename}")
    return logger

# Initialize logging
logger = setup_logging()

# Removed Unicode emoji handling - using plain text only for .exe compatibility

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
            error_msg = f"CRITICAL EXCEPTION OCCURRED in {func.__name__}:"
            logger.critical(error_msg)
            logger.critical(f"Error: {str(e)}")
            logger.critical(f"Exception Type: {type(e).__name__}")
            logger.critical("Full Traceback:")
            logger.critical(traceback.format_exc())
            logger.critical("INITIATING ULTIMATE SHUTDOWN - Process will terminate automatically...")
            
            # Also print to console for immediate visibility
            print(error_msg)
            print(f"ERROR: {str(e)}")
            print(f"Exception Type: {type(e).__name__}")
            print("\nFull Traceback:")
            traceback.print_exc()
            print(f"\nINITIATING ULTIMATE SHUTDOWN - Process will terminate automatically...")
            
            # Try to clean up resources before shutdown
            try:
                # If this is a method call on a BrandTestToolAutomation instance
                if args and hasattr(args[0], '_cleanup_resources'):
                    logger.info("Attempting emergency resource cleanup...")
                    print("Attempting emergency resource cleanup...")
                    args[0]._cleanup_resources()
            except Exception as cleanup_error:
                logger.error(f"Emergency cleanup failed: {cleanup_error}")
                print(f"Emergency cleanup failed: {cleanup_error}")
            
            logger.critical("=" * 60)
            print("=" * 60)
            
            # Use existing ultimate shutdown mechanism - don't reinvent the wheel
            sys.exit(1)
            
    return wrapper

class BrandTestToolAutomation:
    """Automation class for Brand Test Tool with modular step control"""
    
    def __init__(self):
        logger.info(f"Initializing BrandTestToolAutomation...")
        self.window_title = WindowTitle.MAIN_WINDOW.value
        logger.info(f"Looking for window: '{self.window_title}'")
        
        # Initialize automation helper with the found window handle
        self.automation_helper = ManualAutomationHelper(target_window_title=self.window_title)
        
        if not self.automation_helper or not self.automation_helper.hwnd:
            error_msg = f"ERROR: Failed to find window: '{self.window_title}'"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        self.window_handle = self.automation_helper.hwnd
        self.window_info = self.automation_helper.get_window_info()
        logger.info(f"Found window - Handle: {self.window_handle}")
        logger.info(f"Window info: {self.window_info}")
        
        self.graphics = ScreenOverlay()
        self.project_name = ""
        
        # Configuration storage
        self.config = None
        logger.info("BrandTestToolAutomation initialized successfully")

    def set_config(self, config):
        """Set the automation configuration from the selection dialog"""
        self.config = config
        print(f"Configuration set: {config['test_type']} - {config['execution_mode']}")
        
    def get_config(self):
        """Get the current automation configuration"""
        return self.config
        
    def get_prompt_data(self):
        """Get the loaded prompt and execution data"""
        if not self.config:
            return None
        return {
            'test_type_prompt': self.config.get('test_type_prompt', ''),
            'execution_steps': self.config.get('execution_steps', '')
        }

    def demonstrate_config_usage(self):
        """Demonstrate how to use the configuration throughout automation"""
        if not self.config:
            print("ERROR: No configuration available")
            return
            
        safe_print(f"\n🎯 Using {self.config['test_type']} configuration:")
        safe_print("=" * 50)
        
        # Show test type prompt
        if self.config['test_type_prompt']:
            safe_print(f"📋 {self.config['test_type']} Instructions:")
            safe_print(self.config['test_type_prompt'])
            safe_print()
        
        # Show execution steps if enabled
        if self.config['execution_mode'] == ExecutionMode.START_FROM_CUSTOM and self.config['execution_steps']:
            safe_print("🔧 Execution Steps:")
            safe_print(self.config['execution_steps'])
            safe_print()
        
        # Example of how to use config in automation logic
        test_type = self.config['test_type']
        if test_type == TestType.VISA.value:
            safe_print("🔵 Applying Visa-specific automation logic...")
            # Add Visa-specific logic here
        elif test_type == TestType.MASTERCARD.value:
            safe_print("🔴 Applying Mastercard-specific automation logic...")
            # Add Mastercard-specific logic here
        
        if self.config['execution_mode'] == ExecutionMode.START_FROM_CUSTOM:
            safe_print("⚙️ Applying custom automation steps...")
            # Add custom logic here
        
        safe_print("=" * 50)

    def _cleanup_resources(self):
        """
        Clean up all resources used during automation to ensure proper termination.
        
        Resources cleaned up:
        - Graphics overlays and debug visualizations
        - Window handles and automation helpers
        - Configuration data and memory
        - Temporary files or processes
        """
        print("🧹 Cleaning up automation resources...")
        
        try:
            # Clean up graphics overlay
            if hasattr(self, 'graphics') and self.graphics:
                print("   🎨 Cleaning up graphics overlay...")
                # Close any open overlay windows
                try:
                    self.graphics = None
                except:
                    pass
            
            # Reset automation state 
            print("   🔄 Resetting automation state...")
            self.reset()
            
            # Clear configuration data
            if hasattr(self, 'config') and self.config:
                print("   ⚙️ Clearing configuration data...")
                self.config = None
            
            # Force garbage collection to free memory
            print("   🗑️ Performing garbage collection...")
            import gc
            gc.collect()
            
            print("   ✅ Resource cleanup completed")
            
        except Exception as e:
            print(f"   ⚠️ Warning: Some resources may not have been cleaned up properly: {e}")

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
            
            # Make the window background Start at selected Questions
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
    
    def export_file_done(self):
        """Export the file to local folder"""
        
        print('Exporting file started...')
        # opens the dialog to select file
        # Export dialog
        self.automation_helper._bring_to_focus()
        time.sleep(1)
        self.send_navigation_keys('{Alt+F} -> {Down 3} -> {Enter}')
        
        time.sleep(1)
        if not (etpp := ManualAutomationHelper(target_window_title="Export TPP Package Wizard")):
            print("❌ No Export TPP Package Wizard window found")
            return False

        # this etpp window is to be using this bounding box {l:411 t:141 r:922 b:596}
        etpp.setup_window(bbox=(411, 141, 922, 596))
        time.sleep(1)
        
        # playing export sequence
        print("🔍 Playing export sequence...")
        success = play_sequence("export_tpp_file", blocking=True, project_name=self.project_name)
        if not success:
            print("❌ Failed to run sequence")
            return False
        
        print("🎉 Export sequence completed successfully!")
        # now we can just play sequence to export and save the changes
    
    def create_new_project(self):
        """Create a new project"""
        print("🚀 Starting {self.window_title} automation...")
        
        # generate a random project name and save this in self so that when exporting we use the same name to save the file with
        self.project_name = f"sample_test_project_{int(time.time())}"
        
        # Send navigation keys to create project
        if not self.send_navigation_keys(navigation_path="{Alt+F} -> {Down 1} -> {Enter}"):
            return False
        
        time.sleep(0.5)
        
        # Run sequence to fill in project name and description
        print("🎬 Running sequence to fill project details...")
        success = play_sequence("fill_project_details", blocking=True, project_name=self.project_name)
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
        
        max_iterations = 7  # Maximum consecutive failed attempts
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
        
        #now that all tree is collapsed, just send one right key to ensure the root is focussed
        automation_helper.keys("{Right}")
        
        print("🎉 Tree collapse process completed!")

    def prepare_project_setup_window(self):
        """Identify the project setup window. Then ready the treeview for navigation"""
        # Now the Project Settings Window is open
        # Search for a new window
        project_setup_window_handle = ManualAutomationHelper(target_window_title=WindowTitle.PROJECT_SETTINGS.value, title_starts_with=True)
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
        
        # Clean up resources before exit
        self._cleanup_resources()
        
        print('Task completed. Exiting...')
        exit()
    
    @critical_exception_handler
    def fill_questionnaire_v2(self, questionnaire_window, forms_class=None):
        # Initialize the questionnaire filler with specified forms class
        qf = QuestionnaireFiller(questionnaire_window, forms_class=forms_class)
        forms = qf.questionnaire_forms
        
        # Use execution steps from configuration if available
        execution_steps = None
        if self.config and self.config.get('execution_steps'):
            execution_steps = self.config['execution_steps']
            print("🚀 Execution using steps loaded from configuration:")
        else:
            print("🚀 Execution using default steps:")
        
        qf.execute(execution_steps)
    
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
        
        configuration = self.config["test_type_prompt"]
        # Parse configuration from prompt
        def parse_prompt(prompt_text):
            """Parse prompt text to extract tree options and their test cases"""
            tree_options = {}
            current_tree_option = None
            
            for line in prompt_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("- Tree Option:"):
                    current_tree_option = line.split(":")[1].strip()
                    tree_options[current_tree_option] = []
                elif line.startswith("- Test Case:") and current_tree_option:
                    test_case = line.split(":")[1].strip()
                    tree_options[current_tree_option].append(test_case)
            
            return tree_options
        
        
        tree_options = parse_prompt(configuration)
        print(f"📝 Parsed configuration - Tree Options: {tree_options}")
        
        # Now we are ready to navigate to the node we want to edit
        for tree_option, test_cases in tree_options.items():
            navigator = TreeViewNavigator(automation_helper=project_setup_window_handle, collapse_count=2)
            time.sleep(1.5)
            navigator.navigate_to_path(tree_option)
            for test_case in test_cases:
                time.sleep(0.2)
                project_setup_window_handle.keys("{space}")
                time.sleep(1) # gives time for the right panel to get populated
                
                if test_case == "VisaL3Testing_Series01_Build_021":
                    questionnaire_window = start_questionnaire(project_setup_window_handle, questionnaire_window_title="Edit EMVCo L3 Test Session - Questionnaire")
                    if not questionnaire_window:
                        print("❌ No questionnaire window found")
                        return False
                    
                    time.sleep(1)
        
                    # Option 1: Use default forms with manual method calls
                    self.fill_questionnaire_v2(questionnaire_window)
                else:
                    print(f"🔴 Test case {test_case} not implemented yet")

        # click on the apply ok on the Project Settings window
        print('Attempting to click on apply/ok on Project Settings window')
        time.sleep(2)
        
        # we are recapturing the window as it could have been stale by this time.
        if not (pwin:= ManualAutomationHelper(target_window_title=WindowTitle.PROJECT_SETTINGS.value, title_starts_with=True)):
            print("❌ No project settings window found")
            return False
        
        # Get bottom 1/4 region to avoid false positives with similar buttons in middle of window
        from utils.common import get_bottom_quarter_region
        search_region = get_bottom_quarter_region(pwin.get_bbox())
        click_apply_ok_button(pwin, search_region=search_region)
        
        print("✅ BTT Automation completed successfully!")
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


# CUSTOM_MODE is now controlled by the selection dialog

class BTTSelectionDialog:
    """
    Selection dialog for Brand Test Tool automation configuration.
    
    Features:
    - Dropdown for test type selection (Visa, Mastercard, etc.)
    - Dropdown for execution mode selection
    - Automatic prompt file loading based on selection
    - Extensible design for adding more card types
    """
    
    def __init__(self):
        self.root = None
        self.result = None
        self.test_type_var = None
        self.execution_mode_var = None
        
        # Available test types (extensible)
        self.test_types = [TestType.VISA.value, TestType.MASTERCARD.value]
        self.default_test_type = TestType.VISA.value
        
        # Execution modes with display names
        self.execution_mode_display = {
            ExecutionMode.START_FROM_BEGINNING: "Start from Beginning",
            ExecutionMode.START_FROM_QUESTIONNAIRE: "Start from Start Questionnaire", 
            ExecutionMode.START_FROM_CUSTOM: "Start at selected Questions",
            ExecutionMode.EXPORT_TEST: "Export Test"
        }
        self.execution_modes = list(self.execution_mode_display.values())
        self.default_execution_mode = self.execution_mode_display[ExecutionMode.START_FROM_BEGINNING]
        
        # Prompt data storage
        self.test_type_prompt = ""
        self.execution_steps = ""
        
    def _load_prompt_file(self, filename):
        """Load content from a prompt file"""
        try:
            # Use proper path handling for .exe compatibility
            def get_app_data_path(relative_path):
                if getattr(sys, 'frozen', False):
                    # Running as .exe - use directory where .exe is located
                    app_dir = os.path.dirname(sys.executable)
                else:
                    # Development mode - use current directory
                    app_dir = os.path.abspath(".")
                return os.path.join(app_dir, relative_path)
            
            filepath = get_app_data_path(os.path.join('prompts', 'btt', filename))
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                print(f"WARNING: Prompt file not found: {filepath}")
                return ""
        except Exception as e:
            print(f"ERROR: Error loading prompt file {filename}: {e}")
            return ""
    
    def _load_prompts(self):
        """Load prompts based on current selections"""
        # Load test type prompt
        test_type = self.test_type_var.get().lower()
        test_type_filename = f"{test_type}_prompt.txt"
        self.test_type_prompt = self._load_prompt_file(test_type_filename)
        
        # Load execution steps based on execution mode
        execution_mode_display = self.execution_mode_var.get()
        # Find the enum key for the selected display value
        execution_mode_enum = None
        for enum_key, display_value in self.execution_mode_display.items():
            if display_value == execution_mode_display:
                execution_mode_enum = enum_key
                break
        
        if execution_mode_enum == ExecutionMode.START_FROM_CUSTOM:
            self.execution_steps = self._load_prompt_file("custom_execution_steps.txt")
        else:
            self.execution_steps = self._load_prompt_file("execution_steps.txt")
    
    def _on_ok(self):
        """Handle OK button click"""
        try:
            # Find the enum key for the selected display value
            execution_mode_display = self.execution_mode_var.get()
            execution_mode_enum = None
            for enum_key, display_value in self.execution_mode_display.items():
                if display_value == execution_mode_display:
                    execution_mode_enum = enum_key
                    break
            
            self._load_prompts()
            
            self.result = {
                'test_type': self.test_type_var.get(),
                'execution_mode': execution_mode_display,
                'custom_mode': execution_mode_enum.value,
                'test_type_prompt': self.test_type_prompt,
                'execution_steps': self.execution_steps
            }
            
            print(f"✅ Selected: {self.result['test_type']}, Mode: {self.result['execution_mode']}")
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _on_cancel(self):
        """Handle Cancel button click"""
        self.result = None
        self.root.quit()
        self.root.destroy()
    
    def _create_dialog(self):
        """Create the selection dialog window"""
        self.root = tk.Tk()
        self.root.title("BTT Automation Configuration")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Make it always on top
        self.root.attributes('-topmost', True)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Test type selection
        ttk.Label(main_frame, text="Select Test Type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.test_type_var = tk.StringVar(value=self.default_test_type)
        test_type_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.test_type_var,
            values=self.test_types,
            state="readonly",
            width=25
        )
        test_type_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Execution mode selection
        ttk.Label(main_frame, text="Select Execution Mode:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.execution_mode_var = tk.StringVar(value=self.default_execution_mode)
        execution_mode_combo = ttk.Combobox(
            main_frame,
            textvariable=self.execution_mode_var,
            values=self.execution_modes,
            state="readonly",
            width=25
        )
        execution_mode_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT)
        
        # Configure column weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def show(self):
        """Show the selection dialog and return the result"""
        try:
            self._create_dialog()
            self.root.mainloop()
            return self.result
        except Exception as e:
            print(f"❌ Error showing selection dialog: {e}")
            return None

@critical_exception_handler
def main():
    """Main execution function with critical exception handling"""
    
    # Show selection dialog first
    logger.info("Starting BTT Automation Configuration...")
    print("Starting BTT Automation Configuration...")
    dialog = BTTSelectionDialog()
    config = dialog.show()
    
    if config is None:
        logger.warning("Configuration cancelled. Exiting...")
        print("Configuration cancelled. Exiting...")
        return
    
    logger.info(f"Configuration selected:")
    logger.info(f"   Test Type: {config['test_type']}")
    logger.info(f"   Execution Mode: {config['execution_mode']}")
    logger.info(f"   Custom Mode: {config['custom_mode']}")
    logger.info(f"   Test Type Prompt Length: {len(config['test_type_prompt'])} chars")
    logger.info(f"   Execution Steps Length: {len(config['execution_steps'])} chars")
    
    print(f"Configuration selected:")
    print(f"   Test Type: {config['test_type']}")
    print(f"   Execution Mode: {config['execution_mode']}")
    print(f"   Custom Mode: {config['custom_mode']}")
    print(f"   Test Type Prompt Length: {len(config['test_type_prompt'])} chars")
    print(f"   Execution Steps Length: {len(config['execution_steps'])} chars")
    
    # Create automation instance
    logger.info("Creating BTT automation instance...")
    print("Creating BTT automation instance...")
    btt_automation = BrandTestToolAutomation()
    
    # Pass configuration to automation
    logger.info("Setting automation configuration...")
    print("Setting automation configuration...")
    btt_automation.set_config(config)
    
    # Demonstrate how configuration is used
    # btt_automation.demonstrate_config_usage()
    
    # Use the custom mode from dialog configuration
    CUSTOM_MODE = config['custom_mode']
    
    if CUSTOM_MODE and CUSTOM_MODE != "":
        
        if CUSTOM_MODE == ExecutionMode.EXPORT_TEST.value:
            print("Exporting test file...")
            btt_automation.automation_helper._bring_to_focus()
            time.sleep(1)
            btt_automation.export_file_done()
            exit(0)
        
        if not (pwin := ManualAutomationHelper(target_window_title=WindowTitle.PROJECT_SETTINGS.value, title_starts_with=True)):
            print("ERROR: No project settings window found")
            exit()
        
        if CUSTOM_MODE == ExecutionMode.START_FROM_CUSTOM.value:
            if not (edit_window := ManualAutomationHelper(target_window_title=WindowTitle.EDIT_QUESTIONNAIRE.value)):
                print("ERROR: No edit window found")
                exit()
            qf = QuestionnaireFiller(edit_window)
            qf.questionnaire_forms.values["testing_contact"] = True
            qf.questionnaire_forms.values["testing_contactless"] = True
            
            # Use execution steps from loaded configuration
            execution_steps = config.get('execution_steps', '')
            if execution_steps:
                print("Using execution steps from configuration file...")
                qf.execute(execution_steps)
            else:
                print("WARNING: No execution steps found in configuration, using default behavior...")
                qf.execute()
                
            # Get bottom 1/4 region to avoid false positives with similar buttons in middle of window
            from utils.common import get_bottom_quarter_region
            search_region = get_bottom_quarter_region(pwin.get_bbox())
            click_apply_ok_button(pwin, search_region=search_region)
            btt_automation.export_file_done()
            
            
            
        elif CUSTOM_MODE == ExecutionMode.START_FROM_QUESTIONNAIRE.value:
            if not (edit_window := start_questionnaire(pwin, questionnaire_window_title=WindowTitle.EDIT_QUESTIONNAIRE.value)):
                print("❌ No edit window found")
                exit()
            qf = QuestionnaireFiller(edit_window)
            btt_automation.fill_questionnaire_v2(edit_window)
            
        print("Custom Mode Execution completed.")
        exit(0)
    
    # Regular automation flow with configuration
    print("\n🚀 Starting regular automation with selected configuration...")
    btt_automation.execute_all_steps()
    
    # at this stage the file is already done, so we can just export it
    print("🚀 Exporting test file...")
    btt_automation.export_file_done()
    
    btt_automation._cleanup_resources()
    
    from tkinter import messagebox
    messagebox.showinfo("Success", "Process completed successfully!")
    exit(0)

# Example usage
if __name__ == "__main__":
    main()