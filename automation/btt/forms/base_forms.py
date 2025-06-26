"""
Base questionnaire forms class.
Contains all standard form methods that can be inherited and customized by child classes.
"""

import time
from automation.btt.helpers import select_countries
from utils.image_scanner import scan_for_image


class BaseQuestionnaireForms:
    """
    Base class for all questionnaire forms.
    Contains standard implementations for all form interactions.
    Child classes can inherit and override specific methods as needed.
    
    When new form screens are needed, add them directly to this base class
    so all child classes automatically inherit the new functionality.
    
    Child classes can also define execution_steps as a string to enable
    declarative form execution via the execute() method.
    """
    
    # Default execution steps - child classes can override this
    execution_steps = """
country: United States
processor_name: Fiserv
user_tester_information: Tester, Tester@thoughtfocus.com
testing_details: true, true
deployment_type: true
merchant_information: true
terminal_atm_information: terminal name, model name, version info
contactless_atm_information: ATM1, ATM2
contact_chip_oda: true, true
contact_only_features: true, true
comment_box: some comment
confirm_final_information:
test_session_name: some test session name
""".strip()
    
    def __init__(self, current_window, questionnaire_filler):
        """
        Initialize the base forms class.
        
        Args:
            current_window: The window automation helper
            questionnaire_filler: The QuestionnaireFiller instance
        """
        self.current_window = current_window
        self.qf = questionnaire_filler
    
    def parse_execution_steps(self, steps_text=None):
        """
        Parse the execution steps text into a list of method calls.
        
        Args:
            steps_text (str): Optional steps text. If None, uses self.execution_steps
            
        Returns:
            list: List of tuples (method_name, args)
        """
        if steps_text is None:
            steps_text = self.execution_steps
        
        if not steps_text or not steps_text.strip():
            return []
        
        parsed_steps = []
        
        for line in steps_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            if ':' not in line:
                print(f"⚠️ Skipping malformed line: {line}")
                continue
            
            method_name, args_str = line.split(':', 1)
            method_name = method_name.strip()
            args_str = args_str.strip()
            
            # Parse arguments
            args = []
            if args_str:
                # Split by comma and clean up
                raw_args = [arg.strip() for arg in args_str.split(',')]
                for arg in raw_args:
                    # Convert string representations to proper types
                    if arg.lower() == 'true':
                        args.append(True)
                    elif arg.lower() == 'false':
                        args.append(False)
                    elif arg.lower() == 'none':
                        args.append(None)
                    elif arg.startswith('[') and arg.endswith(']'):
                        # Handle list format: [item1, item2]
                        list_items = arg[1:-1].split(',')
                        args.append([item.strip() for item in list_items if item.strip()])
                    else:
                        args.append(arg)
            
            parsed_steps.append((method_name, args))
        
        return parsed_steps
    
    def execute(self, steps_text=None):
        """
        Execute the defined execution steps.
        
        Args:
            steps_text (str): Optional custom steps text. If None, uses self.execution_steps
            
        Returns:
            bool: True if all steps completed successfully
        """
        if not self.execution_steps and not steps_text:
            print("ℹ️ No execution steps defined, skipping auto-execution")
            return True
        
        steps = self.parse_execution_steps(steps_text)
        
        if not steps:
            print("ℹ️ No valid execution steps found")
            return True
        
        print(f"🚀 Starting execution of {len(steps)} steps...")
        
        for step_num, (method_name, args) in enumerate(steps, 1):
            # Check if method exists
            if not hasattr(self, method_name):
                print(f"❌ Step {step_num}: Method '{method_name}' not found on {self.__class__.__name__}")
                return False
            
            # Get the method and call it
            method = getattr(self, method_name)
            print(f"🔄 Step {step_num}: Executing {method_name}({', '.join(map(str, args))})")
            
            try:
                result = method(*args) if args else method()
                if result is False:
                    print(f"❌ Step {step_num}: {method_name} failed")
                    return False
                print(f"✅ Step {step_num}: {method_name} completed successfully")
            except Exception as e:
                print(f"❌ Step {step_num}: {method_name} failed with error: {e}")
                return False
        
        print(f"🎉 All {len(steps)} steps completed successfully!")
        return True
        
    def country(self, country_list=None):
        """
        Select countries from the multi-list view.
        """
        if not self.qf.parse_and_execute_sequence("__0.2,tab,tab"):
            return False
        if not select_countries(self.current_window, country_list):
            print("❌ Failed to select countries")
            return False
        if not self.qf.parse_and_execute_sequence("tab,tab,space"):
            return False
        return True
    
    def processor_name(self, processor_name="Fiserv"):
        """
        Processor name - single text input.
        """
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def user_tester_information(self, name="Tester", email="Tester@thoughtfocus.com"):
        """
        User/tester information - 2 text inputs, one name and one email.
        """
        sequence = f"__0.2,tab,tab,{name},tab,tab,{email},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def testing_details(self, check_first=True, check_second=True):
        """
        Testing details - two checkboxes and an extra button for more information.
        """
        sequence = "__0.2,tab,tab"
        if check_first:
            sequence += ",{space}"
        sequence += ",tab"
        if check_second:
            sequence += ",{space}"
        sequence += ",tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def deployment_type(self, use_dropdown=True):
        """
        Deployment type - dropdown input, down arrow to select the item.
        """
        if use_dropdown:
            return self.qf.parse_and_execute_sequence("__0.2,tab,tab,{down},__0.2,tab,space")
        else:
            return self.qf.parse_and_execute_sequence("__0.2,tab,tab,tab,space")
    
    def merchant_information(self, skip_optional=True):
        """
        Merchant Information with optional field of 1 text input.
        """
        if skip_optional:
            return self.qf.parse_and_execute_sequence("tab,tab,tab,space")
        else:
            # Could be extended to fill optional field if needed
            return self.qf.parse_and_execute_sequence("tab,tab,tab,space")
    
    def terminal_atm_information(self, terminal_name="terminal name", model_name="model name", version_info="version info"):
        """
        Terminal ATM/Information - 3 text inputs and an extra button after each input.
        """
        sequence = f"__0.2,tab,tab,{terminal_name},tab,tab,tab,{model_name},tab,tab,tab,{version_info},tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def contactless_atm_information(self, atm1_name="ATM1", atm2_name="ATM2"):
        """
        Contactless ATM Information - 2 text inputs, one extra button after each input.
        """
        sequence = f"__0.2,tab,tab,{atm1_name},tab,tab,{atm2_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def contact_chip_oda(self, select_first=True, select_second=True):
        """
        Contact chip offline data authentication (ODA) - radio input with conditional button.
        """
        sequence = "__0.2,tab,tab"
        if select_first:
            sequence += ",{space}"
        if select_second:
            sequence += ",{down}"
        sequence += ",(img:oda-screen.png,tab),tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def contact_only_features(self, select_first_set=True, select_second_set=True):
        """
        Contact Only features - 2 sets of radio inputs.
        """
        sequence = "__0.2,tab,tab"
        if select_first_set:
            sequence += ",{space}"
        sequence += ",tab,tab"
        if select_second_set:
            sequence += ",{space}"
        sequence += ",tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def comment_box(self, comment="some comment"):
        """
        Comment box - single text input.
        """
        sequence = f"__0.2,tab,tab,{comment},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def confirm_final_information(self):
        """
        Final information screen - confirm button (special handling required).
        """
        time.sleep(0.2)
        confirm_information_button_location = scan_for_image("confirm-information-button.png", self.current_window.get_bbox(), threshold=0.8)
        if confirm_information_button_location:
            self.current_window.click(confirm_information_button_location)
            return True
        else:
            print("❌ No confirm information button found")
            return False
    
    def test_session_name(self, session_name="some test session name"):
        """
        Test Session Name - single text input.
        """
        sequence = f"__0.2,tab,tab,{session_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence) 