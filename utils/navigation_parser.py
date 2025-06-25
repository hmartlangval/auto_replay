import re
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class NavigationParser:
    """Global parser for navigation paths with keyboard codes and text."""
    
    @staticmethod
    def parse_navigation_path(navigation_path):
        """Parse navigation path with curly bracket notation.
        
        Args:
            navigation_path: Navigation string like:
                - "{Alt+F} -> {N}" (keyboard codes only)
                - "{Alt+F} -> Create Project" (mixed)
                - "File -> New Project" (text only)
                - "{Ctrl+N}" (single shortcut)
                - "{Down 3}" (repeat key)
                
        Returns:
            List of step dictionaries with 'type' and 'value' keys
        """
        try:
            print(f"🔍 Parsing navigation: '{navigation_path}'")
            
            # Split by arrow notation
            parts = [part.strip() for part in navigation_path.split('->')]
            steps = []
            
            for part in parts:
                step = NavigationParser._parse_single_step(part)
                if step:
                    steps.append(step)
                    print(f"  📝 Parsed step: {step}")
            
            return steps
            
        except Exception as e:
            print(f"⚠️ Error parsing navigation path: {e}")
            return []
    
    @staticmethod
    def _parse_single_step(step_text):
        """Parse a single navigation step.
        
        Args:
            step_text: Single step like "{Alt+F}", "{N}", "{Down 2}", "Create Project"
            
        Returns:
            Dict with step information
        """
        step_text = step_text.strip()
        
        # Check if it's a keyboard code (wrapped in curly brackets)
        if step_text.startswith('{') and step_text.endswith('}'):
            code_content = step_text[1:-1]  # Remove { and }
            return NavigationParser._parse_keyboard_code(code_content)
        
        # Check if it's a menu name (common menu names)
        menu_names = ['file', 'edit', 'view', 'format', 'tools', 'help', 'window', 'actions', 'configuration']
        if step_text.lower() in menu_names:
            return {
                'type': 'menu_text',
                'value': step_text.lower(),
                'original': step_text,
                'description': f"Find menu: '{step_text}'"
            }
        
        # Otherwise, it's a menu item text
        return {
            'type': 'menu_item_text',
            'value': step_text.lower(),
            'original': step_text,
            'description': f"Find menu item: '{step_text}'"
        }
    
    @staticmethod
    def _parse_keyboard_code(code_content):
        """Parse keyboard code content (without curly brackets).
        
        Args:
            code_content: Content like "Alt+F", "N", "Down 3", "Ctrl+Shift+S"
            
        Returns:
            Dict with keyboard code information
        """
        code_content = code_content.strip()
        
        # Check for repeat patterns like "Down 3", "Up 2", "Tab 5"
        repeat_match = re.match(r'^(Down|Up|Left|Right|Tab|Enter|Escape)\s+(\d+)$', code_content, re.IGNORECASE)
        if repeat_match:
            key_name = repeat_match.group(1).lower()
            repeat_count = int(repeat_match.group(2))
            return {
                'type': 'key_repeat',
                'key': key_name,
                'count': repeat_count,
                'original': code_content,
                'description': f"Press {key_name} {repeat_count} times"
            }
        
        # Check for modifier combinations like "Alt+F", "Ctrl+N", "Ctrl+Shift+S"
        if '+' in code_content:
            parts = [part.strip() for part in code_content.split('+')]
            modifiers = []
            key = None
            
            for part in parts:
                part_lower = part.lower()
                if part_lower in ['ctrl', 'alt', 'shift', 'win']:
                    modifiers.append(part_lower)
                else:
                    key = part_lower
            
            if key:
                return {
                    'type': 'key_combination',
                    'modifiers': modifiers,
                    'key': key,
                    'original': code_content,
                    'description': f"Press {' + '.join(modifiers + [key])}"
                }
        
        # Single key press
        return {
            'type': 'key_single',
            'key': code_content.lower(),
            'original': code_content,
            'description': f"Press key: '{code_content}'"
        }
    
    @staticmethod
    def execute_step(step, automation_driver):
        """Execute a parsed navigation step.
        
        Args:
            step: Step dictionary from parse_navigation_path
            automation_driver: WebDriver instance
            
        Returns:
            bool: Success/failure
        """
        try:
            print(f"  🎯 Executing: {step['description']}")
            actions = ActionChains(automation_driver)
            
            if step['type'] == 'key_single':
                # Map special keys to Selenium Keys
                key_map = {
                    'enter': Keys.ENTER,
                    'escape': Keys.ESCAPE,
                    'tab': Keys.TAB,
                    'space': Keys.SPACE,
                    'backspace': Keys.BACKSPACE,
                    'delete': Keys.DELETE,
                    'home': Keys.HOME,
                    'end': Keys.END,
                    'pageup': Keys.PAGE_UP,
                    'pagedown': Keys.PAGE_DOWN,
                    'f1': Keys.F1, 'f2': Keys.F2, 'f3': Keys.F3, 'f4': Keys.F4,
                    'f5': Keys.F5, 'f6': Keys.F6, 'f7': Keys.F7, 'f8': Keys.F8,
                    'f9': Keys.F9, 'f10': Keys.F10, 'f11': Keys.F11, 'f12': Keys.F12
                }
                
                selenium_key = key_map.get(step['key'], step['key'])
                actions.send_keys(selenium_key).perform()
                time.sleep(0.3)
                return True
                
            elif step['type'] == 'key_combination':
                # Press modifiers down
                for modifier in step['modifiers']:
                    if modifier == 'ctrl':
                        actions.key_down(Keys.CONTROL)
                    elif modifier == 'alt':
                        actions.key_down(Keys.ALT)
                    elif modifier == 'shift':
                        actions.key_down(Keys.SHIFT)
                
                # Press main key
                actions.send_keys(step['key'])
                
                # Release modifiers
                for modifier in reversed(step['modifiers']):
                    if modifier == 'ctrl':
                        actions.key_up(Keys.CONTROL)
                    elif modifier == 'alt':
                        actions.key_up(Keys.ALT)
                    elif modifier == 'shift':
                        actions.key_up(Keys.SHIFT)
                
                actions.perform()
                time.sleep(0.5)
                return True
                
            elif step['type'] == 'key_repeat':
                key_map = {
                    'down': Keys.ARROW_DOWN,
                    'up': Keys.ARROW_UP,
                    'left': Keys.ARROW_LEFT,
                    'right': Keys.ARROW_RIGHT,
                    'tab': Keys.TAB,
                    'enter': Keys.ENTER,
                    'escape': Keys.ESCAPE
                }
                
                selenium_key = key_map.get(step['key'])
                if selenium_key:
                    for i in range(step['count']):
                        actions.send_keys(selenium_key).perform()
                        time.sleep(0.2)
                    return True
                else:
                    print(f"  ❌ Unknown repeat key: {step['key']}")
                    return False
                    
            elif step['type'] in ['menu_text', 'menu_item_text']:
                # These need to be handled by the specific automation handlers
                # Return True to indicate parsing success, actual execution happens elsewhere
                return True
                
            else:
                print(f"  ❌ Unknown step type: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Step execution failed: {e}")
            return False

