import time
import tkinter as tk

from utils.image_scanner import scan_for_image
from utils.windows_automation import ManualAutomationHelper

def show_result_dialog(root, message):
    """
    Show a reusable modal result dialog for displaying messages.
    """
    # Show results in a scrollable message box
    result_dialog = tk.Toplevel(root)
    result_dialog.title("Results")
    result_dialog.geometry("600x500")
    result_dialog.configure(bg='#2C3E50')
    result_dialog.transient(root)
    result_dialog.grab_set()
    
    # Center the dialog
    result_dialog.update_idletasks()
    x = (result_dialog.winfo_screenwidth() // 2) - (600 // 2)
    y = (result_dialog.winfo_screenheight() // 2) - (500 // 2)
    result_dialog.geometry(f"600x500+{x}+{y}")
    
    # Create scrollable text area
    main_frame = tk.Frame(result_dialog, bg='#2C3E50')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Text widget with scrollbar
    text_frame = tk.Frame(main_frame, bg='#2C3E50')
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget = tk.Text(
        text_frame,
        font=("Consolas", 10),
        bg='#34495E',
        fg='white',
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        relief='flat',
        bd=5
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar.config(command=text_widget.yview)
    
    # Insert results
    text_widget.insert(tk.END, message)
    text_widget.config(state=tk.DISABLED)
    
    # Close button
    close_button = tk.Button(
        main_frame,
        text="Close",
        command=result_dialog.destroy,
        font=("Arial", 10, "bold"),
        bg="#E74C3C",
        fg="white",
        relief='flat',
        width=10,
        height=1,
        cursor='hand2'
    )
    close_button.pack(pady=(10, 0))
    
    # Bind Escape to close
    result_dialog.bind('<Escape>', lambda e: result_dialog.destroy())
    

def show_modal_input_dialog(root, title, prompt, initial_value=""):
    """
    Show a reusable modal input dialog for getting user text input.
    
    Args:
        title: Dialog window title
        prompt: Prompt text to show user
        initial_value: Default/initial value in input field
        
    Returns:
        str or None: User input text, or None if cancelled
    """
    # Create modal dialog window
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.configure(bg='#34495E')
    
    # Make it modal
    dialog.transient(root)
    dialog.grab_set()
    
    # Center the dialog on the screen
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"400x200+{x}+{y}")
    
    # Variable to store result
    result = [None]
    
    # Create dialog content
    main_frame = tk.Frame(dialog, bg='#34495E', padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Prompt label
    prompt_label = tk.Label(
        main_frame,
        text=prompt,
        font=("Arial", 12),
        fg="white",
        bg='#34495E',
        wraplength=350,
        justify='left'
    )
    prompt_label.pack(pady=(0, 15))
    
    # Input entry
    entry = tk.Entry(
        main_frame,
        font=("Arial", 12),
        width=40,
        relief='flat',
        bd=5
    )
    entry.pack(pady=(0, 20))
    entry.insert(0, initial_value)
    entry.focus_set()
    entry.select_range(0, tk.END)
    
    # Buttons frame
    buttons_frame = tk.Frame(main_frame, bg='#34495E')
    buttons_frame.pack()
    
    def on_ok():
        result[0] = entry.get().strip()
        dialog.destroy()
    
    def on_cancel():
        result[0] = None
        dialog.destroy()
    
    # OK button
    ok_button = tk.Button(
        buttons_frame,
        text="OK",
        command=on_ok,
        font=("Arial", 10, "bold"),
        bg="#27AE60",
        fg="white",
        relief='flat',
        width=8,
        height=1,
        cursor='hand2'
    )
    ok_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # Cancel button
    cancel_button = tk.Button(
        buttons_frame,
        text="Cancel",
        command=on_cancel,
        font=("Arial", 10, "bold"),
        bg="#E74C3C",
        fg="white",
        relief='flat',
        width=8,
        height=1,
        cursor='hand2'
    )
    cancel_button.pack(side=tk.LEFT)
    
    # Bind Enter and Escape keys
    dialog.bind('<Return>', lambda e: on_ok())
    dialog.bind('<Escape>', lambda e: on_cancel())
    entry.bind('<Return>', lambda e: on_ok())
    
    # Wait for dialog to close
    dialog.wait_window()
    
    return result[0]


def click_apply_ok_button(window_title: str):
    """
    Click on the Apply OK button using centralized animated image detection.
    """
    window = ManualAutomationHelper(target_window_title=window_title, title_starts_with=True)
    if not window:
        print(f"❌ No window found for {window_title}")
        return
    
    # Wait a moment for any ongoing animations to settle
    time.sleep(0.3)
    
    # Get bounding box and convert from (left, top, right, bottom) to (x, y, width, height)
    bbox = window.get_bbox()
    left, top, right, bottom = bbox
    bounding_box = (left, top, right - left, bottom - top)
    
    print(f"🔍 Window bbox: {bbox} -> converted to: {bounding_box}")
    
    # Use the centralized image scanner with animated_image=True
    from utils.image_scanner import scan_for_image
    
    # Find Apply button using animated search
    apply_location = scan_for_image(
        "apply-btn-normal.png", 
        bounding_box,  # Now properly converted
        threshold=0.8, 
        animated_image=True
    )
    
    # Find OK button using animated search  
    ok_location = scan_for_image(
        "ok-btn-normal.png", 
        bounding_box,  # Now properly converted
        threshold=0.8, 
        animated_image=True
    )
    
    # Click buttons if both found
    if apply_location and ok_location:
        print("🖱️ Clicking Apply button...")
        window.click(apply_location)
        time.sleep(0.3)  # Wait between clicks
        
        print("🖱️ Clicking OK button...")
        window.click(ok_location)
        print("✅ Successfully clicked Apply and OK buttons")
    else:
        missing = []
        if not apply_location:
            missing.append("Apply")
        if not ok_location:
            missing.append("OK")
        print(f"❌ Could not find {', '.join(missing)} button(s)")
        
    return window

