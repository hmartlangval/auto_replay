import re
import time


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
    def execute_step_windows(step, automation_helper):
        """Execute a parsed navigation step using Windows API.
        
        Args:
            step: Step dictionary from parse_navigation_path
            automation_helper: ManualAutomationHelper instance
            
        Returns:
            bool: Success/failure
        """
        import time  # Ensure time is available
        try:
            print(f"  🎯 Executing: {step['description']}")
            
            if step['type'] == 'key_single':
                # Single key press using Windows API
                key_name = step['key'].lower()
                
                # Map common keys to their Windows virtual key codes
                key_map = {
                    'enter': 0x0D,      # VK_RETURN
                    'escape': 0x1B,     # VK_ESCAPE
                    'tab': 0x09,        # VK_TAB
                    'space': 0x20,      # VK_SPACE
                    'backspace': 0x08,  # VK_BACK
                    'delete': 0x2E,     # VK_DELETE
                    'home': 0x24,       # VK_HOME
                    'end': 0x23,        # VK_END
                    'pageup': 0x21,     # VK_PRIOR
                    'pagedown': 0x22,   # VK_NEXT
                    'up': 0x26,         # VK_UP
                    'down': 0x28,       # VK_DOWN
                    'left': 0x25,       # VK_LEFT
                    'right': 0x27,      # VK_RIGHT
                    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
                    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
                    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B
                }
                
                # Use automation helper's existing key functionality
                if key_name in key_map:
                    # For special keys, create a key combination string
                    key_string = f"{{{step['key']}}}"
                    return automation_helper.keys(key_string)
                else:
                    # For regular letters/numbers, just send them directly
                    return automation_helper.keys(step['key'])
                
            elif step['type'] == 'key_combination':
                # Key combination using Windows API
                modifiers_str = '+'.join(step['modifiers'])
                key_string = f"{{{modifiers_str}+{step['key']}}}"
                return automation_helper.keys(key_string)
                
            elif step['type'] == 'key_repeat':
                # Repeat key presses
                key_string = f"{{{step['key']}}}"
                for i in range(step['count']):
                    success = automation_helper.keys(key_string)
                    if not success:
                        return False
                    time.sleep(0.1)  # Small delay between repeats
                return True
                
            elif step['type'] in ['menu_text', 'menu_item_text']:
                # For menu navigation, we could implement text search later
                # For now, just indicate success
                print(f"  ℹ️  Menu navigation not yet implemented: {step['description']}")
                return True
                
            else:
                print(f"  ❌ Unknown step type: {step['type']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Step execution failed: {e}")
            return False

