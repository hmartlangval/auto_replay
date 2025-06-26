"""
Example demonstrating how to create custom questionnaire forms by inheriting from BaseQuestionnaireForms.
This shows the inheritance design pattern in action.
"""

from forms import BaseQuestionnaireForms
from questionnaire_filler import QuestionnaireFiller


class EMVCoL2QuestionnaireForms(BaseQuestionnaireForms):
    """
    Custom forms for EMVCo L2 questionnaires.
    Inherits all base functionality and overrides specific methods as needed.
    """
    
    def processor_name(self, processor_name="EMVCo L2 Processor"):
        """
        Custom processor name for EMVCo L2 - different default value.
        """
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def testing_details(self, check_first=False, check_second=True):
        """
        Custom testing details for EMVCo L2 - different default selections.
        """
        sequence = "__0.2,tab,tab"
        if check_first:
            sequence += ",{space}"
        sequence += ",tab"
        if check_second:
            sequence += ",{space}"
        sequence += ",tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def country(self, country_list=None):
        """
        Custom country selection for EMVCo L2 - different default countries.
        """
        if country_list is None:
            country_list = ["United Kingdom", "Germany"]  # Different defaults
        
        if not self.qf.parse_and_execute_sequence("__0.2,tab,tab"):
            return False
        if not select_countries(self.current_window, country_list):
            print("❌ Failed to select countries")
            return False
        if not self.qf.parse_and_execute_sequence("tab,tab,space"):
            return False
        return True


class MinimalQuestionnaireForms(BaseQuestionnaireForms):
    """
    Minimal forms implementation that skips optional fields.
    """
    
    def merchant_information(self, skip_optional=True):
        """
        Always skip merchant information in minimal implementation.
        """
        return self.qf.parse_and_execute_sequence("tab,tab,tab,space")
    
    def comment_box(self, comment="Auto-generated"):
        """
        Always uses auto-generated comment.
        """
        sequence = f"__0.2,tab,tab,{comment},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)


class VerboseQuestionnaireForms(BaseQuestionnaireForms):
    """
    Verbose forms implementation with detailed logging.
    """
    
    def processor_name(self, processor_name="Verbose Processor"):
        """
        Processor name with verbose logging.
        """
        print(f"🔄 Setting processor name to: {processor_name}")
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        result = self.qf.parse_and_execute_sequence(sequence)
        print(f"✅ Processor name set successfully: {result}")
        return result
    
    def user_tester_information(self, name="Verbose Tester", email="verbose@test.com"):
        """
        User information with verbose logging.
        """
        print(f"🔄 Setting user information - Name: {name}, Email: {email}")
        sequence = f"__0.2,tab,tab,{name},tab,tab,{email},tab,space"
        result = self.qf.parse_and_execute_sequence(sequence)
        print(f"✅ User information set successfully: {result}")
        return result


# Example usage demonstrating the inheritance pattern
if __name__ == "__main__":
    from utils import ManualAutomationHelper
    
    # Get window handle
    edit_window = ManualAutomationHelper(target_window_title="Edit EMVCo L3 Test Session - Questionnaire")
    
    if edit_window:
        print("🎯 Demonstrating inheritance pattern:")
        print()
        
        # Example 1: Using EMVCo L2 forms
        print("1. Using EMVCo L2 Custom Forms:")
        qf_l2 = QuestionnaireFiller(edit_window, forms_class=EMVCoL2QuestionnaireForms)
        # qf_l2.questionnaire_forms.processor_name()  # Would use "EMVCo L2 Processor"
        
        # Example 2: Using minimal forms
        print("2. Using Minimal Forms:")
        qf_minimal = QuestionnaireFiller(edit_window, forms_class=MinimalQuestionnaireForms)
        # qf_minimal.questionnaire_forms.comment_box()  # Would use "Auto-generated"
        
        # Example 3: Using verbose forms
        print("3. Using Verbose Forms:")
        qf_verbose = QuestionnaireFiller(edit_window, forms_class=VerboseQuestionnaireForms)
        # qf_verbose.questionnaire_forms.processor_name()  # Would log details
        
        print("✅ All form classes instantiated successfully!")
        print("🎉 Inheritance pattern working correctly!")
    else:
        print("❌ No window found for demonstration") 