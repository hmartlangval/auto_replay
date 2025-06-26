"""
EMVCo L2 Questionnaire Forms.
Specialized implementation for EMVCo L2 test questionnaires.
"""

from .base_forms import BaseQuestionnaireForms
from automation.btt.helpers import select_countries


class EMVCoL2QuestionnaireForms(BaseQuestionnaireForms):
    """
    EMVCo L2 specific questionnaire forms.
    Override methods to customize for L2 testing requirements.
    """
    
    def processor_name(self, processor_name="EMVCo L2 Processor"):
        """
        EMVCo L2 processor name with specific default.
        """
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def country(self, country_list=None):
        """
        EMVCo L2 country selection - different default countries for L2 testing.
        """
        if country_list is None:
            country_list = ["United Kingdom", "Germany", "France"]
        
        if not self.qf.parse_and_execute_sequence("__0.2,tab,tab"):
            return False
        if not select_countries(self.current_window, country_list):
            print("❌ Failed to select countries")
            return False
        if not self.qf.parse_and_execute_sequence("tab,tab,space"):
            return False
        return True
    
    def user_tester_information(self, name="EMVCo L2 Tester", email="l2.tester@emvco.com"):
        """
        EMVCo L2 user information with specific defaults.
        """
        sequence = f"__0.2,tab,tab,{name},tab,tab,{email},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def test_session_name(self, session_name="EMVCo L2 Test Session"):
        """
        EMVCo L2 test session name with specific default.
        """
        sequence = f"__0.2,tab,tab,{session_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence) 