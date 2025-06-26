"""
EMVCo L1 Questionnaire Forms.
Specialized implementation for EMVCo L1 test questionnaires.
"""

from .base_forms import BaseQuestionnaireForms


class EMVCoL1QuestionnaireForms(BaseQuestionnaireForms):
    """
    EMVCo L1 specific questionnaire forms.
    Override methods to customize for L1 testing requirements.
    """
    
    def processor_name(self, processor_name="EMVCo L1 Processor"):
        """
        EMVCo L1 processor name with specific default.
        """
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def testing_details(self, check_first=True, check_second=False):
        """
        EMVCo L1 testing details - different default checkbox selections.
        """
        sequence = "__0.2,tab,tab"
        if check_first:
            sequence += ",{space}"
        sequence += ",tab"
        if check_second:
            sequence += ",{space}"
        sequence += ",tab,tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
    
    def test_session_name(self, session_name="EMVCo L1 Test Session"):
        """
        EMVCo L1 test session name with specific default.
        """
        sequence = f"__0.2,tab,tab,{session_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence) 