# BTT Automation Configuration

This directory contains configuration files for the Brand Test Tool (BTT) automation system.

## Overview

The BTT automation now supports configurable test types and custom steps through a selection dialog that appears when the automation starts.

## Configuration Files

### Test Type Prompts
- `visa_prompt.txt` - Visa-specific test configurations and instructions
- `mastercard_prompt.txt` - Mastercard-specific test configurations and instructions
- `custom_prompt.txt` - Custom automation steps and configurations

## How to Use

1. **Start BTT Automation**: Run the `btt.py` script
2. **Selection Dialog**: A dialog window will appear with:
   - **Test Type Dropdown**: Choose between Visa, Mastercard, or other card types
   - **Use Custom Steps Checkbox**: Enable to include custom automation steps
3. **Automatic Loading**: The system automatically loads the appropriate prompt files based on your selection
4. **Configuration Usage**: The loaded configuration is used throughout the automation process

### Testing

To test the dialog functionality without running full automation:
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

## File Format

Prompt files should contain:
- Configuration parameters
- Test-specific instructions
- Automation guidelines
- Any card-specific requirements

Example format:
```
Card Name Test Configuration:
- Use card-specific testing protocols
- Enable relevant payment features
- Configure appropriate CVMs
- Set merchant category codes
- Test with specific currencies
```

## Configuration Object

The configuration object passed to automation contains:
- `test_type`: Selected card type (e.g., "Visa", "Mastercard")
- `use_custom`: Boolean indicating if custom steps are enabled
- `test_type_prompt`: Content from the card-specific prompt file
- `custom_prompt`: Content from custom_prompt.txt (if enabled)

## Usage in Automation Code

```python
# Access configuration
config = btt_automation.get_config()
test_type = config['test_type'].lower()

# Use card-specific logic
if test_type == 'visa':
    # Visa-specific automation
elif test_type == 'mastercard':
    # Mastercard-specific automation

# Use custom steps
if config['use_custom']:
    # Apply custom automation steps
```

## Future Enhancements

- Add more card types (American Express, Discover, etc.)
- Support for multiple prompt files per card type
- Dynamic prompt loading based on test scenarios
- Integration with external configuration systems 