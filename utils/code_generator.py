"""
Code generation utilities for sequence recorder
Contains all the static code generation functions
"""
import os
from datetime import datetime


def generate_file_header(sequence_name, screen_info):
    """Generate the file header with metadata"""
    header = []
    header.append(f'"""Auto-generated sequence: {sequence_name}"""')
    header.append(f'# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    header.append(f'# Screen Resolution: {screen_info["width"]}x{screen_info["height"]}')
    header.append(f'# DPI: {screen_info["dpi_x"]}x{screen_info["dpi_y"]} (Scale: {screen_info["dpi_scale"]:.1f}x)')
    header.append(f'# Platform: {screen_info["platform"]}')
    header.append('')
    return '\n'.join(header)


def generate_imports(screen_info):
    """Generate the import statements"""
    imports = []
    imports.append('import time')
    imports.append('import tkinter as tk')
    imports.append('from tkinter import messagebox')
    imports.append('import platform')
    imports.append('try:')
    imports.append('    from pynput.mouse import Button, Listener as MouseListener')
    imports.append('    from pynput.keyboard import Key, Listener as KeyboardListener')
    imports.append('    import pynput.mouse as mouse_control')
    imports.append('    import pynput.keyboard as keyboard_control')
    imports.append('except ImportError:')
    imports.append('    print("pynput library required. Install with: pip install pynput")')
    imports.append('    exit(1)')
    imports.append('')
    
    # Add Windows DPI detection code if needed
    if screen_info['platform'] == 'Windows':
        imports.append('# Windows-specific imports for DPI detection')
        imports.append('if platform.system() == "Windows":')
        imports.append('    try:')
        imports.append('        import ctypes')
        imports.append('        WINDOWS_DPI_AVAILABLE = True')
        imports.append('    except ImportError:')
        imports.append('        WINDOWS_DPI_AVAILABLE = False')
        imports.append('else:')
        imports.append('    WINDOWS_DPI_AVAILABLE = False')
        imports.append('')
    
    return '\n'.join(imports)


def generate_screen_detection_function(screen_info):
    """Generate the screen detection function"""
    func_lines = []
    func_lines.append('def get_current_screen_info():')
    func_lines.append('    """Get current screen resolution and DPI information"""')
    func_lines.append('    screen_info = {}')
    func_lines.append('    ')
    func_lines.append('    # Get screen resolution')
    func_lines.append('    try:')
    func_lines.append('        temp_root = tk.Tk()')
    func_lines.append('        temp_root.withdraw()')
    func_lines.append('        screen_info["width"] = temp_root.winfo_screenwidth()')
    func_lines.append('        screen_info["height"] = temp_root.winfo_screenheight()')
    func_lines.append('        temp_root.destroy()')
    func_lines.append('    except:')
    func_lines.append('        screen_info["width"] = 1920')
    func_lines.append('        screen_info["height"] = 1080')
    func_lines.append('    ')
    
    if screen_info['platform'] == 'Windows':
        func_lines.append('    # Get DPI information (Windows)')
        func_lines.append('    if WINDOWS_DPI_AVAILABLE:')
        func_lines.append('        try:')
        func_lines.append('            user32 = ctypes.windll.user32')
        func_lines.append('            user32.SetProcessDPIAware()')
        func_lines.append('            dc = user32.GetDC(0)')
        func_lines.append('            dpi_x = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)')
        func_lines.append('            dpi_y = ctypes.windll.gdi32.GetDeviceCaps(dc, 90)')
        func_lines.append('            user32.ReleaseDC(0, dc)')
        func_lines.append('            screen_info["dpi_x"] = dpi_x')
        func_lines.append('            screen_info["dpi_y"] = dpi_y')
        func_lines.append('            screen_info["dpi_scale"] = dpi_x / 96.0')
        func_lines.append('        except:')
        func_lines.append('            screen_info["dpi_x"] = 96')
        func_lines.append('            screen_info["dpi_y"] = 96')
        func_lines.append('            screen_info["dpi_scale"] = 1.0')
    else:
        func_lines.append('    # Fallback DPI for non-Windows')
        func_lines.append('    screen_info["dpi_x"] = 96')
        func_lines.append('    screen_info["dpi_y"] = 96')
        func_lines.append('    screen_info["dpi_scale"] = 1.0')
    
    func_lines.append('    ')
    func_lines.append('    screen_info["platform"] = platform.system()')
    func_lines.append('    return screen_info')
    func_lines.append('')
    
    return '\n'.join(func_lines)


def generate_validation_function(screen_info):
    """Generate the screen validation function"""
    func_lines = []
    func_lines.append('def validate_screen_compatibility():')
    func_lines.append('    """Check if current screen settings match recorded settings"""')
    func_lines.append('    recorded_settings = {')
    func_lines.append(f'        "width": {screen_info["width"]},')
    func_lines.append(f'        "height": {screen_info["height"]},')
    func_lines.append(f'        "dpi_x": {screen_info["dpi_x"]},')
    func_lines.append(f'        "dpi_y": {screen_info["dpi_y"]},')
    func_lines.append(f'        "dpi_scale": {screen_info["dpi_scale"]:.2f},')
    func_lines.append(f'        "platform": "{screen_info["platform"]}"')
    func_lines.append('    }')
    func_lines.append('    ')
    func_lines.append('    current_settings = get_current_screen_info()')
    func_lines.append('    ')
    func_lines.append('    mismatches = []')
    func_lines.append('    if current_settings["width"] != recorded_settings["width"] or current_settings["height"] != recorded_settings["height"]:')
    func_lines.append('        res_msg = f"Resolution: Recorded {recorded_settings[\'width\']}x{recorded_settings[\'height\']}, Current {current_settings[\'width\']}x{current_settings[\'height\']}"')
    func_lines.append('        mismatches.append(res_msg)')
    func_lines.append('    ')
    func_lines.append('    if abs(current_settings["dpi_scale"] - recorded_settings["dpi_scale"]) > 0.1:')
    func_lines.append('        dpi_msg = f"DPI Scale: Recorded {recorded_settings[\'dpi_scale\']:.1f}x, Current {current_settings[\'dpi_scale\']:.1f}x"')
    func_lines.append('        mismatches.append(dpi_msg)')
    func_lines.append('    ')
    func_lines.append('    if current_settings["platform"] != recorded_settings["platform"]:')
    func_lines.append('        platform_msg = f"Platform: Recorded {recorded_settings[\'platform\']}, Current {current_settings[\'platform\']}"')
    func_lines.append('        mismatches.append(platform_msg)')
    func_lines.append('    ')
    func_lines.append('    return mismatches')
    func_lines.append('')
    
    return '\n'.join(func_lines)


def generate_action_code(action):
    """Generate code for a single action"""
    code_lines = []
    
    if action['type'] == 'mouse_click':
        code_lines.append(f'    # Mouse click at ({action["x"]}, {action["y"]})')
        code_lines.append(f'    mouse.position = ({action["x"]}, {action["y"]})')
        code_lines.append(f'    mouse.click(Button.{action["button"].lower()})')
    elif action['type'] == 'key_press':
        key_combo = action['key']
        code_lines.append(f'    # Key combination: {key_combo}')
        
        if '+' in key_combo:
            # Key combination (e.g., ctrl+r)
            parts = key_combo.split('+')
            modifiers = parts[:-1]
            base_key = parts[-1]
            
            # Press modifiers
            for mod in modifiers:
                code_lines.append(f'    keyboard.press(Key.{mod})')
            
            # Press base key
            if base_key in ['enter', 'space', 'tab', 'backspace', 'delete', 'up', 'down', 'left', 'right', 'home', 'end', 'page_up', 'page_down'] or base_key.startswith('f'):
                code_lines.append(f'    keyboard.press(Key.{base_key})')
                code_lines.append(f'    keyboard.release(Key.{base_key})')
            else:
                code_lines.append(f'    keyboard.type("{base_key}")')
            
            # Release modifiers (in reverse order)
            for mod in reversed(modifiers):
                code_lines.append(f'    keyboard.release(Key.{mod})')
        else:
            # Single key
            if key_combo in ['enter', 'space', 'tab', 'backspace', 'delete', 'up', 'down', 'left', 'right', 'home', 'end', 'page_up', 'page_down'] or key_combo.startswith('f'):
                code_lines.append(f'    keyboard.press(Key.{key_combo})')
                code_lines.append(f'    keyboard.release(Key.{key_combo})')
            else:
                code_lines.append(f'    keyboard.type("{key_combo}")')
    
    return code_lines


def generate_replay_function(sequence_name, actions, screen_info):
    """Generate the main replay function"""
    func_lines = []
    func_lines.append(f'def replay_{sequence_name.lower().replace(" ", "_")}():')
    func_lines.append('    """Replay the recorded sequence"""')
    func_lines.append('    # Validate screen compatibility first')
    func_lines.append('    mismatches = validate_screen_compatibility()')
    func_lines.append('    if mismatches:')
    func_lines.append('        error_msg = "Screen settings mismatch detected!\\n\\n"')
    func_lines.append('        error_msg += "This sequence was recorded with different screen settings:\\n"')
    func_lines.append('        for mismatch in mismatches:')
    func_lines.append('            error_msg += mismatch + "\\n"')
    func_lines.append('        error_msg += "\\nReplaying with different settings may cause clicks to miss their targets.\\n"')
    func_lines.append('        error_msg += "Please adjust your screen settings to match the recorded ones, or re-record the sequence."')
    func_lines.append('        ')
    func_lines.append('        try:')
    func_lines.append('            root = tk.Tk()')
    func_lines.append('            root.withdraw()')
    func_lines.append('            messagebox.showerror("Screen Settings Mismatch", error_msg)')
    func_lines.append('            root.destroy()')
    func_lines.append('        except:')
    func_lines.append('            print("ERROR: " + error_msg.replace("\\n", " "))')
    func_lines.append('        return False')
    func_lines.append('    ')
    func_lines.append('    mouse = mouse_control.Controller()')
    func_lines.append('    keyboard = keyboard_control.Controller()')
    func_lines.append('    ')
    func_lines.append(f'    print(f"Starting replay of sequence: {sequence_name}")')
    func_lines.append('    print("Screen settings validated successfully!")')
    func_lines.append('    ')
    
    # Generate action code
    last_time = 0
    for action in actions:
        # Add delay based on timing
        delay = round(action['time'] - last_time, 2)
        if delay > 0:
            func_lines.append(f'    time.sleep({delay})  # Wait {delay}s')
        
        # Generate action code
        action_code = generate_action_code(action)
        func_lines.extend(action_code)
        func_lines.append('')
        
        last_time = action['time']
    
    func_lines.append('    print("Sequence replay completed successfully!")')
    func_lines.append('    return True')
    func_lines.append('')
    
    return '\n'.join(func_lines)


def generate_main_section(sequence_name):
    """Generate the main execution section"""
    main_lines = []
    main_lines.append('if __name__ == "__main__":')
    main_lines.append(f'    success = replay_{sequence_name.lower().replace(" ", "_")}()')
    main_lines.append('    if not success:')
    main_lines.append('        print("Replay failed due to screen settings mismatch.")')
    main_lines.append('        exit(1)')
    
    return '\n'.join(main_lines) 