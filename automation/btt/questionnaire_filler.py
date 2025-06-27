import time
import re
from forms import BaseQuestionnaireForms, DefaultQuestionnaireForms
from utils.image_scanner import scan_for_image


class QuestionnaireFiller:
    """
    A modular class for executing automation sequences using simple text syntax.
    
    Supported syntax:
    - __0.2 : Sleep for 0.2 seconds
    - tab : Press tab key
    - space : Press space key
    - enter : Press enter key
    - down : Press down arrow key
    - up : Press up arrow key
    - {space} : Press space key (alternative syntax)
    - {down} : Press down arrow key (alternative syntax)
    - PlainText : Type the text
    - (img:image_name.png,action) : Conditional action if image is found
    
    Example sequence: "__0.2,tab,tab,Fiserv,tab,space,(img:oda-screen.png,tab)"
    """
    
    def __init__(self, automation_helper, forms_class=None):
        """
        Initialize the questionnaire filler with an automation helper and forms class.
        
        Args:
            automation_helper: ManualAutomationHelper instance for window automation
            forms_class: Class that inherits from BaseQuestionnaireForms to handle form interactions.
                        If None, uses DefaultQuestionnaireForms.
        """
        self.automation_helper = automation_helper
        
        # Use provided forms class or default
        if forms_class is None:
            forms_class = DefaultQuestionnaireForms
        
        # Validate that the forms class inherits from BaseQuestionnaireForms
        if not issubclass(forms_class, BaseQuestionnaireForms):
            raise ValueError(f"forms_class must inherit from BaseQuestionnaireForms, got {forms_class}")
        
        # Instantiate the forms class
        self.questionnaire_forms = forms_class(self.automation_helper, self)
    
    def execute(self, steps_text=None):
        """
        Execute the questionnaire forms using the defined execution steps.
        
        Args:
            steps_text (str): Optional custom steps text. If None, uses forms' execution_steps
            
        Returns:
            bool: True if all steps completed successfully
        """
        return self.questionnaire_forms.execute(steps_text)
        
    def parse_and_execute_sequence(self, sequence_text):
        """
        Parse and execute a sequence of automation commands.
        
        Args:
            sequence_text (str): Comma-separated sequence of commands
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Split by comma but preserve content inside parentheses
            commands = self._smart_split_sequence(sequence_text)
            
            for command in commands:
                if not command:
                    continue
                    
                success = self._execute_command(command)
                if not success:
                    print(f"❌ Failed to execute command: {command}")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"❌ Error executing sequence: {e}")
            return False
    
    def _smart_split_sequence(self, sequence_text):
        """
        Split sequence by commas but preserve content inside parentheses.
        
        Args:
            sequence_text (str): Comma-separated sequence
            
        Returns:
            list: List of commands with parentheses content preserved
        """
        commands = []
        current_command = ""
        paren_depth = 0
        
        for char in sequence_text:
            if char == '(':
                paren_depth += 1
                current_command += char
            elif char == ')':
                paren_depth -= 1
                current_command += char
            elif char == ',' and paren_depth == 0:
                # Only split on comma if we're not inside parentheses
                if current_command.strip():
                    commands.append(current_command.strip())
                current_command = ""
            else:
                current_command += char
        
        # Add the last command
        if current_command.strip():
            commands.append(current_command.strip())
        
        return commands
    
    def _execute_command(self, command):
        """
        Execute a single command.
        
        Args:
            command (str): Single command to execute
            
        Returns:
            bool: True if successful, False otherwise
        """
        command = command.strip()
        
        # Handle sleep commands (__0.2)
        if command.startswith('__'):
            try:
                sleep_time = float(command[2:])
                time.sleep(sleep_time)
                return True
            except ValueError:
                print(f"❌ Invalid sleep command: {command}")
                return False
        
        # Handle conditional commands (img:name,action)
        if command.startswith('(') and command.endswith(')'):
            return self._execute_conditional_command(command[1:-1])
        
        # Handle key commands with braces {space}, {down}, etc.
        if command.startswith('{') and command.endswith('}'):
            key = command[1:-1].lower()
            return self._press_key(key)
        
        # Handle simple key commands
        if command.lower() in ['tab', 'space', 'enter', 'down', 'up', 'left', 'right']:
            return self._press_key(command.lower())
        
        # Handle text input (anything else is considered text to type)
        return self._type_text(command)
    
    def _execute_conditional_command(self, condition):
        """
        Execute a conditional command based on image detection.
        
        Args:
            condition (str): Condition in format "img:image_name,action"
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Parse condition: img:image_name,action
            if not condition.startswith('img:'):
                print(f"❌ Invalid conditional command: {condition}")
                return False
            
            parts = condition.split(',', 1)
            if len(parts) != 2:
                print(f"❌ Invalid conditional format: {condition}")
                return False
            
            image_part = parts[0]  # img:image_name
            action = parts[1].strip()  # action to execute
            
            # Extract image name
            image_name = image_part[4:]  # Remove 'img:' prefix
            
            # Get bounding box and convert from (left, top, right, bottom) to (x, y, width, height)
            bbox = self.automation_helper.get_bbox()
            left, top, right, bottom = bbox
            bounding_box = (left, top, right - left, bottom - top)
            
            # Check if image exists using animated search for better reliability
            image_location = scan_for_image(image_name, bounding_box, threshold=0.8, animated_image=True)
            
            if image_location:
                print(f"✅ Image '{image_name}' found, executing action: {action}")
                return self._execute_command(action)
            else:
                print(f"ℹ️ Image '{image_name}' not found, skipping action: {action}")
                return True  # Not finding the image is not a failure
                
        except Exception as e:
            print(f"❌ Error executing conditional command: {e}")
            return False
    
    def _press_key(self, key):
        """
        Press a specific key.
        
        Args:
            key (str): Key name to press
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key_mapping = {
                'tab': '{tab}',
                'space': '{space}',
                'enter': '{enter}',
                'down': '{down}',
                'up': '{up}',
                'left': '{left}',
                'right': '{right}'
            }
            
            key_code = key_mapping.get(key.lower(), f'{{{key}}}')
            self.automation_helper.keys(key_code)
            time.sleep(0.1)  # Small delay between key presses
            return True
            
        except Exception as e:
            print(f"❌ Error pressing key '{key}': {e}")
            return False
    
    def _type_text(self, text):
        """
        Type text into the current field.
        
        Args:
            text (str): Text to type
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.automation_helper.type(text)
            time.sleep(0.1)  # Small delay after typing
            return True
            
        except Exception as e:
            print(f"❌ Error typing text '{text}': {e}")
            return False
    
    def execute_multi_tab_sequence(self, tab_count, followed_by_space=False, followed_by_enter=False):
        """
        Execute multiple tab presses followed by optional space or enter.
        Helper method for common patterns.
        
        Args:
            tab_count (int): Number of tab presses
            followed_by_space (bool): Whether to press space after tabs
            followed_by_enter (bool): Whether to press enter after tabs
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create sequence string
            sequence_parts = ['tab'] * tab_count
            
            if followed_by_space:
                sequence_parts.append('space')
            if followed_by_enter:
                sequence_parts.append('enter')
            
            sequence = ','.join(sequence_parts)
            return self.parse_and_execute_sequence(sequence)
            
        except Exception as e:
            print(f"❌ Error executing multi-tab sequence: {e}")
            return False
        
    