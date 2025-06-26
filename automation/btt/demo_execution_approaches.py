"""
Demo: Three Different Approaches to Form Execution

This demonstrates the flexibility of the forms system:
1. Manual method calls (existing approach)
2. Declarative execution using execution_steps
3. Custom execution steps from files or strings
"""

from questionnaire_filler import QuestionnaireFiller
from forms import DefaultQuestionnaireForms, CustomQuestionnaireForms
from utils import ManualAutomationHelper


def demo_manual_approach():
    """
    Approach 1: Manual method calls (existing approach)
    Maximum flexibility, full control over each step
    """
    print("🎯 Demo 1: Manual Method Calls")
    print("=" * 50)
    
    edit_window = ManualAutomationHelper(target_window_title="Test Window")
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
    
    edit_window = ManualAutomationHelper(target_window_title="Test Window")
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
    
    edit_window = ManualAutomationHelper(target_window_title="Test Window")
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
country: Algeria, Morocco
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
    
    edit_window = ManualAutomationHelper(target_window_title="Test Window")
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
    print("country: Algeria, Morocco")
    print("processor_name: My Processor")
    print("testing_details: true, false")
    print("confirm_final_information:")
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
    
    show_execution_steps_examples()
    
    # Run demos (commented out since they need actual window)
    # demo_manual_approach()
    # demo_declarative_approach() 
    # demo_custom_declarative_approach()
    # demo_file_based_execution()
    
    print("💡 Summary:")
    print("1. Manual: Maximum flexibility, step-by-step control")
    print("2. Declarative: Simple automation, predefined steps")
    print("3. Custom: Different forms with their own steps")
    print("4. File-based: External configuration, easy to modify")
    print()
    print("🎉 All approaches work together - choose what fits your needs!") 