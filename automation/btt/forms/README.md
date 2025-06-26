# BTT Forms Package

This package contains all questionnaire forms classes for the Brand Test Tool automation.

## Structure

```
forms/
├── __init__.py                 # Package initialization and exports
├── base_forms.py              # BaseQuestionnaireForms - parent class
├── default_forms.py           # DefaultQuestionnaireForms - standard implementation
├── custom_forms.py            # CustomQuestionnaireForms - example customization
├── emvco_l1_forms.py         # EMVCo L1 specific forms
├── emvco_l2_forms.py         # EMVCo L2 specific forms
├── form_template_generator.py # Utility to generate new forms
└── README.md                  # This documentation
```

## Base Class

**`BaseQuestionnaireForms`** - Contains all standard form methods:
- `country()` - Country selection
- `processor_name()` - Processor name input
- `user_tester_information()` - User and email inputs
- `testing_details()` - Testing checkboxes
- `deployment_type()` - Deployment dropdown
- `merchant_information()` - Merchant info
- `terminal_atm_information()` - Terminal info
- `contactless_atm_information()` - Contactless info
- `contact_chip_oda()` - ODA settings
- `contact_only_features()` - Contact features
- `comment_box()` - Comment input
- `confirm_final_information()` - Confirmation button
- `test_session_name()` - Session name input

## Creating New Forms

### Method 1: Manual Creation
```python
from .base_forms import BaseQuestionnaireForms

class MyCustomForms(BaseQuestionnaireForms):
    def processor_name(self, processor_name="My Custom Processor"):
        sequence = f"__0.2,tab,tab,{processor_name},tab,space"
        return self.qf.parse_and_execute_sequence(sequence)
```

### Method 2: Using Template Generator
```python
from forms.form_template_generator import create_form_file

create_form_file(
    "MyCustom", 
    "Description of the custom form",
    ["processor_name", "test_session_name"]
)
```

## Usage Pattern

```python
from automation.btt.questionnaire_filler import QuestionnaireFiller
from automation.btt.forms import EMVCoL1QuestionnaireForms

# Initialize with specific forms class
qf = QuestionnaireFiller(edit_window, forms_class=EMVCoL1QuestionnaireForms)

# Method 1: Call methods directly
qf.questionnaire_forms.processor_name("EMVCo L1 Processor")
qf.questionnaire_forms.country(["United States", "Canada"])

# Method 2: Use declarative execution
qf.execute()  # Uses the class's predefined execution_steps
```

## Declarative Execution Format

You can define form execution steps as simple text configuration:

```python
execution_steps = """
# Simple parameter format - comma-separated
processor_name: Fiserv
user_tester_information: Tester, Tester@thoughtfocus.com
testing_details: true, false

# Array format - use [item1, item2, item3] for lists
country: [United States, Canada, Mexico]

# No parameters
confirm_final_information:

# Comments are supported
# deployment_type: true
"""
```

### Parsing Rules

- **Array format**: Use `[item1, item2, item3]` for methods expecting lists
- **Multiple parameters**: Use comma-separated values `param1, param2, param3`
- **Boolean values**: Use `true`, `false`, `none` (case-insensitive)
- **Comments**: Lines starting with `#` are ignored
- **Method calls**: Format is `method_name: arguments`

### Examples

```
# Single parameter
processor_name: Custom Processor

# Multiple parameters
user_tester_information: John Doe, john@example.com

# Array/list parameter
country: [United States, Canada, United Kingdom]

# Boolean parameters
testing_details: true, false
deployment_type: false

# No parameters
confirm_final_information:
```

## Upcoming Forms (15-20 planned)

1. **EMVCoL3QuestionnaireForms** - EMVCo L3 test questionnaires
2. **VisaContactlessQuestionnaireForms** - Visa contactless payment forms
3. **MasterCardContactlessQuestionnaireForms** - MasterCard contactless forms
4. **AmexContactlessQuestionnaireForms** - American Express contactless forms
5. **DiscoverContactlessQuestionnaireForms** - Discover contactless forms
6. **PBOCQuestionnaireForms** - PBOC (People's Bank of China) forms
7. **JCBQuestionnaireForms** - JCB payment forms
8. **UnionPayQuestionnaireForms** - UnionPay payment forms
9. **VisaDPANQuestionnaireForms** - Visa DPAN forms
10. **MasterCardDPANQuestionnaireForms** - MasterCard DPAN forms
11. **TokenizedPaymentQuestionnaireForms** - Tokenized payment forms
12. **MobileWalletQuestionnaireForms** - Mobile wallet forms
13. **ApplePayQuestionnaireForms** - Apple Pay specific forms
14. **GooglePayQuestionnaireForms** - Google Pay specific forms
15. **SamsungPayQuestionnaireForms** - Samsung Pay specific forms
16. **PayPalQuestionnaireForms** - PayPal integration forms
17. **RegionalEMVQuestionnaireForms** - Regional EMV compliance forms
18. **PCIQuestionnaireForms** - PCI compliance forms
19. **ATMWithdrawalQuestionnaireForms** - ATM withdrawal forms
20. **PinVerificationQuestionnaireForms** - PIN verification forms

## Design Principles

1. **Inheritance** - All forms inherit from `BaseQuestionnaireForms`
2. **Override Only What's Different** - Only customize methods that need changes
3. **Consistent Naming** - Use `{FormType}QuestionnaireForms` naming pattern
4. **Default Values** - Provide sensible defaults for each form type
5. **Documentation** - Document what each override does and why

## Adding New Forms

1. Create new file: `{formtype}_forms.py`
2. Import base class: `from .base_forms import BaseQuestionnaireForms`
3. Inherit and override needed methods
4. Add to `__init__.py` exports
5. Update this README

## Best Practices

- **Only override methods that need customization**
- **Use meaningful default values**
- **Add docstrings explaining the customization**
- **Test each new forms class thoroughly**
- **Keep method signatures consistent with base class** 