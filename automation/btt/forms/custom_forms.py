"""
Custom questionnaire forms example.
Shows how to inherit from BaseQuestionnaireForms and override specific methods.
"""

import sys
import os

# Add paths to allow imports when running directly  
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .base_forms import BaseQuestionnaireForms

# Try relative import first, then absolute
try:
    from ..helpers import select_countries
except ImportError:
    from helpers import select_countries


class CustomQuestionnaireForms(BaseQuestionnaireForms):
    """
    Example of a custom questionnaire forms class that overrides specific methods.
    Also demonstrates custom execution steps.
    """
    
    # Custom execution steps - different from base class
    execution_steps = """
# Custom form execution steps
country: Canada, Mexico
processor_name: Custom Processor
user_tester_information: Custom Tester, custom@test.com
testing_details: false, true
deployment_type: false
merchant_information: false
terminal_atm_information: Custom Terminal, Custom Model, v2.0
contactless_atm_information: CATM1, CATM2
contact_chip_oda: false, true
contact_only_features: true, false
comment_box: Custom automation comment
confirm_final_information:
test_session_name: Custom Test Session
""".strip()
    
    def processor_name(self, processor_name="Custom Processor"):
        """
        Custom processor name implementation - different default value.
        """
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def country(self, country_list=None):
        """
        Custom country selection - different default countries.
        """
        if country_list is None:
            country_list = ["Canada"]  # Different default
        
        if not self.qf.parse_and_execute_sequence("__0.2,tab,tab"):
            return False
        if not select_countries(self.current_window, country_list):
            print("❌ Failed to select countries")
            return False
        if not self.qf.parse_and_execute_sequence("tab,tab,space"):
            return False
        return True 