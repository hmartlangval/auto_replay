"""
Base questionnaire forms class.
Contains all standard form methods that can be inherited and customized by child classes.
"""

import time
import sys
import os

# Add paths to allow imports when running directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Try relative import first, then absolute
try:
    from ..helpers import select_countries
except ImportError:
    from helpers import select_countries

# Make image scanner import optional
try:
    from utils.image_scanner import scan_for_image
except ImportError:
    print("⚠️ Warning: image_scanner not available (missing cv2 dependency)")
    def scan_for_image(*args, **kwargs):
        print("❌ scan_for_image not available - install opencv-python")
        return None


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
    
    # ui_label_mapping = """
    # UI Navigation Hierarchy
    # region_selection
    #   country
    # acquirer_information
    #   processor_name
    # user_tester_information
    #   contact_name
    #   contact_email
    # testing
    #   contact_testing
    #   contactless_testing
    # deployment_type
    #   deployment_type
    # terminal_implementation
    #   quick_chip
    # visa_products_accepted
    #   common_debit_aid_supported
    #   interlink_supported_on_contact
    #   interlink_supported_on_contactless
    # merchant_information
    #   merchant_name
    # terminal_atm_information
    #   terminal_name
    #   terminal_model
    #   payment_app_name_version
    # contactless_atm_information
    #   contactless_atm_information
    # 2. Processor Name
    # 3. User/Tester Information
    # 4. Testing Details
    # 5. Deployment Type
    # 6. Merchant Information
    # """
    
    
    # Default execution steps - child classes can override this
    execution_steps = """
# Use [item1, item2] format for methods expecting lists
country: [United States, Canada]
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
        self.values = {
            "testing_contact": False,
            "testing_contactless": False
        }
    
    def parse_execution_steps(self, steps_text=None):
        """
        Parse the execution steps text into a list of method calls.
        
        Parsing rules:
        - If argument contains [item1, item2, item3] format, parse as array/list
        - Otherwise, split by comma for multiple parameters
        - Convert true/false/none to proper Python types
        
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
            
            # Parse arguments using simplified approach
            args = []
            if args_str:
                # Check if the entire argument string is an array format
                if args_str.startswith('[') and args_str.endswith(']'):
                    # Parse as array: [item1, item2, item3] -> ["item1", "item2", "item3"]
                    list_items = args_str[1:-1].split(',')
                    array_items = [item.strip() for item in list_items if item.strip()]
                    args.append(array_items)
                else:
                    # Parse as comma-separated parameters
                    raw_args = [arg.strip() for arg in args_str.split(',')]
                    for arg in raw_args:
                        # Convert string representations to proper types
                        if arg.lower() == 'true':
                            args.append(True)
                        elif arg.lower() == 'false':
                            args.append(False)
                        elif arg.lower() == 'none':
                            args.append(None)
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
        self.values["testing_contact"] = check_first
        self.values["testing_contactless"] = check_second
        sequence = "__0.2,tab,tab"
        if check_first:
            sequence += ",{space}"
        sequence += ",tab"
        if check_second:
            sequence += ",{space}"
        sequence += ",tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def deployment_type(self, dropdown_down_count: str = "0"):
        """
        Deployment type - dropdown input, down arrow to select the item.
        """
        try:
            dropdown_down_count = int(dropdown_down_count)
        except ValueError:
            print(f"❌ Invalid dropdown count value: {dropdown_down_count}")
            return False
        
        # Get number of down presses needed based on index
        down_sequence = ",{down}" * dropdown_down_count if dropdown_down_count > 0 else ""
        
        sequence = f"__0.2,tab,tab{down_sequence},__0.2,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def merchant_information(self, value:str = ""):
        """
        Merchant Information with optional field of 1 text input.
        """
        sequence = "__0.2,tab,tab"
        
        value = value.strip()
        
        if value != "":
            sequence += f"{value}"
        
        sequence += ",tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
       
    
    def visa_products_accepted(self, first_true=True, second_true=True, third_true=True):
        """Similar implementation as Reference Number
        There is minimum 2 radio groups, if only one of contact and contactless are true.
        And 3 radio groups if both are true.
        
        """
        first_key = "{space}" if first_true else "{down}"
        second_key = "{space}" if second_true else "{down}"
        third_key = "{space}" if third_true else "{down}"
        
        sequence = f"__0.2,tab,tab,{first_key},tab,tab,{second_key}"
        if self.values["testing_contact"] and self.values["testing_contactless"]:
            sequence += ",tab,tab,{third_key}"
        sequence += ",tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def terminal_implementation(self, isTrue=True):
        if isTrue:
            return self.qf.parse_and_execute_sequence("__0.2,tab,tab,{space},tab,space")
        else:
            return self.qf.parse_and_execute_sequence("__0.2,tab,tab,{down},tab,space")
    
    def terminal_atm_information(self, terminal_name="terminal name", model_name="model name", version_info="version info"):
        """
        Terminal ATM/Information - 3 text inputs and an extra button after each input.
        """
        sequence = f"__0.2,tab,tab,{terminal_name},tab,tab,tab,{model_name},tab,tab,tab,{version_info},tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def reference_number(self, first_value="1", second_value="2", third_value="3", fourth_value="4"):
        """
        Reference number - 
            2 input text + button next to it if testing contact is True
            2 input text + button next (only on first one) to it if testing contactless is True
            And required that ONE Of these will be true or both
        """
        if not (self.values["testing_contact"] or self.values["testing_contactless"]):
            print("❌ Either testing_contact or testing_contactless must be True")
            return False

        # Start sequence with first two inputs for contact testing, guaranteed we have minimum 2 inputs regardless
        sequence = "__0.2,tab,tab{first_value},tab,tab,tab,{second_value}"
        
        # You are now still in the 2nd text input
        if self.values["testing_contactless"]:
            if not self.values["testing_contact"]: # only contactless is true
                pass
            else: # both are true
                sequence += ",tab,tab,tab,{third_value},tab,tab,tab,{fourth_value}"
        else:
            sequence += ",tab" # only contact is trueyou need to be at the next button.
       
        sequence += ",tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def contactless_atm_information(self, atm1_name="ATM1", atm2_name="ATM2"):
        """
        Contactless ATM Information - 2 text inputs, one extra button after each input.
        """
        sequence = f"__0.2,tab,tab,{atm1_name},tab,tab,{atm2_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    
    def __file_test_input_list_forms(self, values:list[str], last_button_tab_count:int = 0, go_next:bool = True):
        """
        Fill the test input list forms with the given values.
        """
        sequence = "__0.2,tab,tab"
        if len(values) == 0:
            # we are skipping this directly without any input
            sequence += ",tab" * last_button_tab_count
        else:        
            for i in range(len(values)):
                sequence = self.__set_text_input_value(sequence, values[i], last_button_tab_count if i == len(values)-1 else 2)
        if go_next:
            sequence += ",tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def __set_text_input_value(self, sequence: str, value: str, followed_by_tab_count: int = 0):
        """
        Set the text input value to the given value.
        """
        sequence += f"{value}"
        sequence += ",{tab}" * followed_by_tab_count
        return sequence
    
    def __fill_radio_list_forms(self, values:list[bool], last_button_tab_count:int = 0, go_next:bool = True):
        """
        Fill the radio forms with the given values.
        """
        sequence = "__0.2,tab,tab"
        for i in range(len(values)):
            sequence = self.__set_radio_value(sequence, values[i], last_button_tab_count if i == len(values)-1 else 2)
        if go_next:
            sequence += ",tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
            
    def __set_radio_value(self, sequence: str, isTrue: bool, followed_by_tab_count: int = 0):
        """
        Set the radio value to True or False.
        """
        if isTrue:
            sequence += ",{space}"
        else:
            sequence += ",{down}"
        sequence += ",{tab}" * followed_by_tab_count
        return sequence
    
    def __fill_dropdown_list_forms(self, values:list[str], last_button_tab_count:int = 0, go_next:bool = True):
        """
        Fill the dropdown forms with the given values.
        """
        sequence = "__0.2,tab,tab"
        for i in range(len(values)):
            sequence = self.__set_dropdown_value(sequence, values[i], last_button_tab_count if i == len(values)-1 else 2)
        if go_next:
            sequence += ",tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
            
    def __set_dropdown_value(self, sequence: str, position_in_list: int = 1, followed_by_tab_count: int = 0):
        """
        Set the dropdown value to the given value.
        """
        sequence += ",{down}" * position_in_list
        sequence += ",{tab}" * followed_by_tab_count
        return sequence
    
    def pin_opt_out_mechanism(self, first_position=1, second_position=1):
        """
        PIN opt-out mechanism - 2 sets of dropdown inputs.
        """
        return self.__fill_dropdown_list_forms([first_position, second_position])
    
    def fleet_2_0(self, first=True):
        """
        Fleet 2.0 - 1 sets of radio inputs.
        """
        return self.__fill_radio_list_forms([first])
    
    def contact_chip_oda(self, isDDA=True):
        """
        Contact chip offline data authentication (ODA) - radio input with conditional button.
        """
        sequence = "__0.2,tab,tab"
        sequence = self.__set_radio_value(sequence, isDDA)
        # if select_second:
        #     sequence += ",{down}"
        # sequence += ",(img:oda-screen.png,tab),tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def contact_chip_cvm(self, first=False, second=False, third=None, fourth=None, fifth=None, sixth=None):
        """
        Contact chip card verification method (CVM) - radio input with conditional button.
        """
        values = [first, second, third, fourth, fifth, sixth]
        return self.__fill_radio_list_forms(values, 1)
    
    def contactless_chip_cvms(self, first=False, second=False, third=None, fourth=None):
        """
        Contactless chip card verification method (CVM) - radio input with conditional button.
        """
        first_set = [first]
        self.__fill_radio_list_forms(first_set, 1, False) # False indicates we are not finishing the page yet
        
        second_set = [second, third, fourth]
        return self.__fill_radio_list_forms(second_set, 1)
    
    def contact_only_features(self, first=True, second=True, third=True):
        """
        Contact Only features - 2 sets of radio inputs.
        """
        values = [first, second, third]
        return self.__fill_radio_list_forms(values)
    
    def contactless_only_features(self, first=True):
        """
        Contactless Only features - 1 set of radio inputs.
        """
        values = [first]
        return self.__fill_radio_list_forms(values)
    
    def comment_box(self, comment=None):
        """
        Comment box - single text input.
        It means skip it if comment is None
        """
        return self.__file_test_input_list_forms(["" if comment is None else comment])
    
    def confirm_final_information(self):
        """
        Final information screen - confirm button (special handling required).
        """
        time.sleep(0.2)
        confirm_information_button_location = scan_for_image("confirm-information-btn.png", self.current_window.get_bbox(), threshold=0.8)
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
    
    def sleep(self, seconds=str):
        """
        Sleep - sleep for the given number of seconds.
        """
        try:
            seconds = float(seconds)
            time.sleep(seconds)
        except ValueError:
            print(f"❌ Invalid seconds value: {seconds}")
            time.sleep(1)
        
        return True
    
    def apply_ok(self):
        """
        Apply OK - apply button then OK button.
        The UI screen has 3 buttons - OK, Cancel and cancel, where OK is current focussed.
        
        Order of key press is Apply first, then OK.
        This will be replaced with image or other reliable approach in future
        
        """
        return self.qf.parse_and_execute_sequence("__0.2,tab,space,{shift+tab},space")