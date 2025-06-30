# BTT Automation Configuration

This directory contains configuration files for the Brand Test Tool (BTT) automation system.

## Overview

The BTT automation now supports configurable test types and custom steps through a selection dialog that appears when the automation starts.

## Configuration Files

### Test Type Prompts (Configuration)
- `visa_prompt.txt` - Visa-specific test configurations and settings
- `mastercard_prompt.txt` - Mastercard-specific test configurations and settings

### Execution Steps (Automation)
- `execution_steps.txt` - Standard automation steps for normal modes
- `custom_execution_steps.txt` - Custom automation steps for "Start at selected Questions" mode

## Key Distinction

**Test Type Prompts** (`visa_prompt.txt`, `mastercard_prompt.txt`):
- Define overall test configuration and settings
- Specify which test cases to run and configuration parameters
- Used to determine automation flow and test selection

**Execution Steps**:
- `execution_steps.txt` - Full automation sequence for normal operation
- `custom_execution_steps.txt` - Subset of steps for custom/partial automation
- Used to control questionnaire filling behavior

## How to Use

1. **Start BTT Automation**: Run the `btt.py` script
2. **Selection Dialog**: A dialog window will appear with:
   - **Test Type Dropdown**: Choose between Visa, Mastercard, or other card types
   - **Execution Mode Dropdown**: Choose how to start the automation:
     - Start from Beginning: Complete automation from start
     - Start from Start Questionnaire: Skip to questionnaire phase
     - Start at selected Questions: Use custom execution steps from external file
3. **Automatic Loading**: The system automatically loads the appropriate prompt files based on your selection
4. **Configuration Usage**: The loaded configuration is used throughout the automation process

### Testing

To test the dialog functionality:
```bash
python examples/test_btt_dialog.py
```

## Adding New Card Types

To add support for a new card type (e.g., "American Express"):

1. **Create Prompt File**: Add `americanexpress_prompt.txt` (or `amex_prompt.txt`) to this directory
2. **Add to Dialog**: Edit the `BTTSelectionDialog` class in `btt.py`:
   ```python
   self.test_types = ["Visa", "Mastercard", "American Express"]
   ```
3. **Add Logic**: Implement card-specific logic in the automation methods

## File Formats

### Test Type Prompt Files
Prompt files should contain:
- Configuration parameters  
- Test-specific instructions
- Tree navigation paths
- Card-specific requirements

Example format:
```
Card Name Test Configuration:
- Tree Option: 1.7.2
- Test Case: VisaL3Testing_Series01_Build_021
- Use card-specific testing protocols
- Enable relevant payment features
```

### Execution Steps File
Execution steps should contain automation commands in this format:
```
# Comments start with #
country: [United States (US)]
processor_name: Test Processor  
user_tester_information: Tester Name, email@test.com
testing_details: true, true
deployment_type: 1
terminal_atm_information: Terminal, Model, Version
contact_chip_oda: true
comment_box: Test comment
confirm_final_information:
apply_ok:
```

## Configuration Object

The configuration object passed to automation contains:
- `test_type`: Selected card type (e.g., "Visa", "Mastercard")
- `execution_mode`: Selected execution mode (e.g., "Start from Beginning", "Start at selected Questions")
- `custom_mode`: Internal mode value ("", "START_FROM_CLICK_START_TEST", "START_FROM_CUSTOM")
- `test_type_prompt`: Content from the card-specific prompt file (configuration)
- `execution_steps`: Content from execution_steps.txt or custom_execution_steps.txt based on execution mode

## Usage in Automation Code

```python
# Access configuration
config = btt_automation.get_config()
test_type = config['test_type'].lower()

# Use card-specific logic based on test type prompts
if test_type == 'visa':
    # Use Visa-specific configuration
elif test_type == 'mastercard':
    # Use Mastercard-specific configuration

# Use execution mode
if config['execution_mode'] == "Start at selected Questions":
    # Use custom execution steps from execution_steps.txt
    execution_steps = config['execution_steps']
    qf.execute(execution_steps)
elif config['execution_mode'] == "Start from Start Questionnaire":
    # Skip to questionnaire phase with default steps
```

## Future Enhancements

- Add more card types (American Express, Discover, etc.)
- Support for multiple prompt files per card type
- Dynamic prompt loading based on test scenarios
- Integration with external configuration systems 