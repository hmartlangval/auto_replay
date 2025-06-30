"""
Demo: Three Different Approaches to Form Execution

This demonstrates the flexibility of the forms system:
1. Manual method calls (existing approach)
2. Declarative execution using execution_steps
3. Custom execution steps from files or strings
"""

import sys
import os


# Add parent directories to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.dirname(__file__))

from questionnaire_filler import QuestionnaireFiller
from forms import DefaultQuestionnaireForms, CustomQuestionnaireForms
from utils import ManualAutomationHelper
from utils.common import click_apply_ok_button

def demo_manual_approach():
    """
    Approach 1: Manual method calls (existing approach)
    Maximum flexibility, full control over each step
    """
    print("🎯 Demo 1: Manual Method Calls")
    print("=" * 50)
    
    edit_window = ManualAutomationHelper(target_window_title="Edit EMVCo", title_starts_with=True)
    if not edit_window:
        print("❌ No window found for demo")
        return
    
    qf = QuestionnaireFiller(edit_window)
    forms = qf.questionnaire_forms
    
    # Manual step-by-step execution
    print("🔄 Manual execution:")
    forms.country(["United States"])
    forms.processor_name("Manual Processor")
    forms.user_tester_information("Manual Tester", "manual@test.com")
    # ... etc
    
    print("✅ Manual approach completed\n")


def demo_declarative_approach():
    """
    Approach 2: Declarative execution using default execution_steps
    Simple, automated, uses predefined steps
    """
    print("🎯 Demo 2: Declarative Execution (Default Steps)")
    print("=" * 50)
    
    edit_window = ManualAutomationHelper(target_window_title="Edit EMVCo", title_starts_with=True)
    if not edit_window:
        print("❌ No window found for demo")
        return
    
    qf = QuestionnaireFiller(edit_window)
    
    # One-line execution using predefined steps
    print("🚀 Declarative execution using default steps:")
    result = qf.execute()
    
    if result:
        print("✅ Declarative approach completed successfully\n")
    else:
        print("❌ Declarative approach failed\n")


def demo_custom_declarative_approach():
    """
    Approach 3: Custom declarative execution
    Uses custom forms class with different execution steps
    """
    print("🎯 Demo 3: Custom Declarative Execution")
    print("=" * 50)
    
    edit_window = ManualAutomationHelper(target_window_title="Edit EMVCo", title_starts_with=True)
    if not edit_window:
        print("❌ No window found for demo")
        return
    
    qf = QuestionnaireFiller(edit_window, forms_class=CustomQuestionnaireForms)
    
    # One-line execution using custom steps
    print("🚀 Declarative execution using custom steps:")
    result = qf.execute()
    
    if result:
        print("✅ Custom declarative approach completed successfully\n")
    else:
        print("❌ Custom declarative approach failed\n")


def demo_file_based_execution():
    """
    Approach 4: File-based execution steps
    Load execution steps from external file (future enhancement)
    """
    print("🎯 Demo 4: File-based Execution (Future)")
    print("=" * 50)
    
    # Example of loading from file (implementation ready for this)
    custom_steps = """
# File-based execution steps
country: [Algeria, Morocco]
processor_name: File-based Processor
user_tester_information: File Tester, file@test.com
testing_details: true, false
deployment_type: true
merchant_information: true
terminal_atm_information: File Terminal, File Model, v3.0
contactless_atm_information: FATM1, FATM2
contact_chip_oda: true, false
contact_only_features: false, true
comment_box: Loaded from file
confirm_final_information:
test_session_name: File-based Test Session
"""
    custom_steps = """
comment_box:
confirm_final_information:
sleep: 2
apply_ok:
# File-based execution steps
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
# contact_chip_oda: true, true, true, false, false, true
# contact_only_features: false, true, false
# contactless_chip_cvms: true, true, true, false
# contactless_only_features: false
# fleet_2_0: false
# comment_box:
# confirm_final_information:
"""
    
    edit_window = ManualAutomationHelper(target_window_title="Edit EMVCo", title_starts_with=True)
    if not edit_window:
        print("❌ No window found for demo")
        return
    
    qf = QuestionnaireFiller(edit_window)
    
    # Execute using custom steps string (could be loaded from file)
    print("🚀 Execution using steps loaded from file/string:")
    result = qf.execute(custom_steps)
    
    if result:
        print("✅ File-based approach completed successfully\n")
    else:
        print("❌ File-based approach failed\n")


def show_execution_steps_examples():
    """Show examples of execution steps format"""
    print("📋 Execution Steps Format Examples")
    print("=" * 50)
    
    print("✅ Valid formats:")
    print("country: United States")
    print("country: Algeria, Morocco")  # Parsed as ["Algeria", "Morocco"]
    print("country: [Canada, Mexico]")  # Explicit list format also works
    print("processor_name: My Processor")
    print("user_tester_information: John Doe, john@email.com")  # Parsed as two args
    print("testing_details: true, false")  # Parsed as boolean args
    print("confirm_final_information:")  # No arguments
    print("# This is a comment")
    print("")
    
    print("❌ Invalid formats:")
    print("country United States (missing colon)")
    print("invalid_method: test (method doesn't exist)")
    print("")


if __name__ == "__main__":
    print("🎯 Forms Execution Approaches Demo")
    print("=" * 50)
    print()
    
    # show_execution_steps_examples()
    
    # Run demos (commented out since they need actual window)
    # demo_manual_approach()
    # demo_declarative_approach() 
    # demo_custom_declarative_approach()
    # demo_file_based_execution()
    
    # At this stage the dialog is OK is already pressed
    # Back to the Project Settings Page, we are going to click on Apply OK again one more time
    # new_project_window = ManualAutomationHelper(target_window_title="Project Settings", title_starts_with=True)
    # if not new_project_window:
    #     print("❌ No window found for demo")
    #     exit()
    
    # Get Project Settings window and use bottom 1/4 region to avoid false positives
    from utils.common import get_bottom_quarter_region
    project_window = ManualAutomationHelper(target_window_title="Project Settings", title_starts_with=True)
    if project_window:
        search_region = get_bottom_quarter_region(project_window.get_bbox())
        click_apply_ok_button(project_window, search_region=search_region)
    else:
        print("❌ No Project Settings window found")
    
    # Try both normal and focused apply button images
    # apply_button_location = scan_for_image("apply-btn-normal.png", new_project_window.get_bbox(), threshold=0.8)
    # if not apply_button_location:
    #     apply_button_location = scan_for_image("apply-btn-focussed.png", new_project_window.get_bbox(), threshold=0.8)
        
    # if apply_button_location:
    #     print(f"Apply button found at {apply_button_location}")
    #     new_project_window.click(apply_button_location)
    # else:
    #     print("Apply button not found")
    
    
    print("💡 Summary:")
    print("1. Manual: Maximum flexibility, step-by-step control")
    print("2. Declarative: Simple automation, predefined steps")
    print("3. Custom: Different forms with their own steps")
    print("4. File-based: External configuration, easy to modify")
    print()
    print("🎉 All approaches work together - choose what fits your needs!") 