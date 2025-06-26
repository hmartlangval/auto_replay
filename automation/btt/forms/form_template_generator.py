"""
Form Template Generator
Utility to generate new questionnaire forms classes quickly.
"""

import os


def generate_form_class(form_name, class_description="", custom_methods=None):
    """
    Generate a new questionnaire forms class file.
    
    Args:
        form_name (str): Name of the form (e.g., "EMVCoL3", "VisaContactless")
        class_description (str): Description of what this form is for
        custom_methods (list): List of method names that should be customized
    
    Returns:
        str: Generated Python code for the forms class
    """
    
    if custom_methods is None:
        custom_methods = ["processor_name", "test_session_name"]
    
    class_name = f"{form_name}QuestionnaireForms"
    
    template = f'''"""
{form_name} Questionnaire Forms.
{class_description}
"""

from .base_forms import BaseQuestionnaireForms


class {class_name}(BaseQuestionnaireForms):
    """
    {form_name} specific questionnaire forms.
    {class_description}
    """
    
'''
    
    # Add custom method templates
    for method in custom_methods:
        if method == "processor_name":
            template += f'''    def processor_name(self, processor_name="{form_name} Processor"):
        """
        {form_name} processor name with specific default.
        """
        sequence = f"__0.2,tab,tab,{{processor_name}},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
'''
        elif method == "test_session_name":
            template += f'''    def test_session_name(self, session_name="{form_name} Test Session"):
        """
        {form_name} test session name with specific default.
        """
        sequence = f"__0.2,tab,tab,{{session_name}},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
'''
        elif method == "country":
            template += f'''    def country(self, country_list=None):
        """
        {form_name} country selection - customize for specific requirements.
        """
        if country_list is None:
            country_list = ["United States"]  # Customize defaults
        
        if not self.qf.parse_and_execute_sequence("__0.2,tab,tab"):
            return False
        if not select_countries(self.current_window, country_list):
            print("❌ Failed to select countries")
            return False
        if not self.qf.parse_and_execute_sequence("tab,tab,space"):
            return False
        return True
    
'''
    
    return template


def create_form_file(form_name, class_description="", custom_methods=None):
    """
    Create a new forms file in the forms directory.
    
    Args:
        form_name (str): Name of the form
        class_description (str): Description of the form
        custom_methods (list): List of methods to customize
    """
    
    code = generate_form_class(form_name, class_description, custom_methods)
    filename = f"{form_name.lower()}_forms.py"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w') as f:
        f.write(code)
    
    print(f"✅ Created {filename}")
    return filepath


# List of upcoming forms (examples for the 15-20 forms)
UPCOMING_FORMS = [
    ("EMVCoL3", "EMVCo L3 test questionnaires"),
    ("VisaContactless", "Visa contactless payment forms"), 
    ("MasterCardContactless", "MasterCard contactless payment forms"),
    ("AmexContactless", "American Express contactless forms"),
    ("DiscoverContactless", "Discover contactless payment forms"),
    ("PBOC", "PBOC (People's Bank of China) forms"),
    ("JCB", "JCB payment forms"),
    ("UnionPay", "UnionPay payment forms"),
    ("VisaDPAN", "Visa DPAN (Device Primary Account Number) forms"),
    ("MasterCardDPAN", "MasterCard DPAN forms"),
    ("TokenizedPayment", "Tokenized payment forms"),
    ("MobileWallet", "Mobile wallet payment forms"),
    ("ApplePay", "Apple Pay specific forms"),
    ("GooglePay", "Google Pay specific forms"),
    ("SamsungPay", "Samsung Pay specific forms"),
    ("PayPal", "PayPal integration forms"),
    ("RegionalEMV", "Regional EMV compliance forms"),
    ("PCI", "PCI compliance forms"),
    ("ATMWithdrawal", "ATM withdrawal transaction forms"),
    ("PinVerification", "PIN verification forms")
]


if __name__ == "__main__":
    print("🎯 Form Template Generator")
    print("This utility helps create new questionnaire forms classes.")
    print()
    
    # Example: Generate a few forms
    print("📝 Example: Generating EMVCo L3 forms...")
    create_form_file(
        "EMVCoL3", 
        "Specialized implementation for EMVCo L3 test questionnaires.",
        ["processor_name", "test_session_name", "country"]
    )
    
    print()
    print("📋 Upcoming Forms List:")
    for i, (form_name, description) in enumerate(UPCOMING_FORMS, 1):
        print(f"{i:2d}. {form_name} - {description}")
    
    print()
    print("💡 To create a new form, use:")
    print("   create_form_file('FormName', 'Description', ['method1', 'method2'])") 