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


def get_bottom_quarter_region(bbox):
    """
    Calculate the bottom 1/4 region of a window bounding box.
    
    Args:
        bbox: Window bounding box as (left, top, right, bottom)
        
    Returns:
        tuple: (search_bbox, search_bounding_box) where:
            - search_bbox: (left, top, right, bottom) for bottom 1/4
            - search_bounding_box: (x, y, width, height) for image scanning
    """
    left, top, right, bottom = bbox
    
    # Calculate bottom 1/4 region
    window_height = bottom - top
    quarter_height = window_height // 4
    bottom_quarter_top = top + (3 * quarter_height)  # Start at 75% down
    
    # Return both formats
    search_bbox = (left, bottom_quarter_top, right, bottom)
    search_bounding_box = (left, bottom_quarter_top, right - left, bottom - bottom_quarter_top)
    
    print(f"📏 Window height: {window_height}px, bottom 1/4 region: {search_bbox}")
    
    return search_bbox, search_bounding_box


def click_apply_ok_button(current_window=None, window_title: str=None, search_region=None):
    """
    Click on the Apply OK button using centralized animated image detection with debug visualization.
    
    Args:
        current_window: Window object to search in
        window_title: Window title to find (if current_window not provided)
        search_region: Optional (search_bbox, search_bounding_box) tuple to search in.
                      If None, searches entire window.
    """
    window = current_window if current_window else ManualAutomationHelper(target_window_title=window_title, title_starts_with=True)
    if not window:
        print(f"❌ No window found for {window_title}")
        return
    
    # Wait a moment for any ongoing animations to settle
    time.sleep(0.3)
    
    # Get bounding box
    bbox = window.get_bbox()
    
    # Use provided search region or entire window
    if search_region:
        search_bbox, search_bounding_box = search_region
        print(f"🎯 Using provided search region: {search_bbox}")
    else:
        # Search entire window
        left, top, right, bottom = bbox
        search_bbox = bbox
        search_bounding_box = (left, top, right - left, bottom - top)
        print(f"🔍 Searching entire window: {search_bbox}")
    
    # Use the centralized image scanner with animated_image=True
    from utils.image_scanner import scan_for_image
    
    # Find Apply button using animated search
    apply_location = scan_for_image(
        "apply-btn-normal.png", 
        search_bounding_box,
        threshold=0.8, 
        animated_image=True
    )
    
    # Find OK button using animated search
    ok_location = scan_for_image(
        "ok-btn-normal.png", 
        search_bounding_box,
        threshold=0.8, 
        animated_image=True
    )
    
    # Show debug visualization using custom button visualization (works without click interference)
    if apply_location and ok_location:
        print("🎯 Showing debug visualization for Apply and OK buttons...")
        _show_button_debug_visualization(search_bbox, apply_location=apply_location, ok_location=ok_location, duration=2)
        time.sleep(0.5)  # Brief pause after visualization
        
        print("🖱️ Clicking Apply button...")
        window.click(apply_location)
        time.sleep(1.0)  # 1 second delay between clicks as requested
        
        print("🖱️ Clicking OK button...")
        window.click(ok_location)
        print("✅ Successfully clicked Apply and OK buttons")
        return True
    else:
        missing = []
        if not apply_location:
            missing.append("Apply")
        if not ok_location:
            missing.append("OK")
        print(f"❌ Could not find {', '.join(missing)} button(s)")
        
        # Show debug visualization even if buttons not found
        _show_button_debug_visualization(search_bbox, apply_location=apply_location, ok_location=ok_location, duration=3)
        return False


def _show_button_debug_visualization(search_region, apply_location=None, ok_location=None, duration=3):
    """Show debug visualization for Apply and OK buttons - CUSTOM IMPLEMENTATION (no click interference)"""
    import tkinter as tk
    import threading
    import time as time_module
    
    def create_and_show():
        # Create a temporary transparent window
        root = tk.Tk()
        root.withdraw()  # Hide initially
        
        # Make it fullscreen and completely transparent
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.attributes('-alpha', 1.0)  # Fully opaque for the shapes
        root.overrideredirect(True)
        
        # Make the window background transparent
        try:
            root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        # Create transparent canvas with black background (which becomes transparent)
        canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw search region rectangle (blue)
        canvas.create_rectangle(
            search_region[0], search_region[1], search_region[2], search_region[3],
            outline='#0066FF', width=3, fill=''
        )
        
        # Draw Apply button bounding box (green rectangle)
        if apply_location:
            x, y = apply_location
            # Estimate button size (typical button dimensions)
            button_width, button_height = 60, 25
            canvas.create_rectangle(
                x - button_width//2, y - button_height//2,
                x + button_width//2, y + button_height//2,
                outline='#00FF00', width=4, fill=''
            )
            # Add label positioned away from click area
            canvas.create_text(x, y-35, text="APPLY", fill='#00FF00', font=('Arial', 12, 'bold'))
        
        # Draw OK button bounding box (orange rectangle)
        if ok_location:
            x, y = ok_location
            # Estimate button size (typical button dimensions)
            button_width, button_height = 50, 25
            canvas.create_rectangle(
                x - button_width//2, y - button_height//2,
                x + button_width//2, y + button_height//2,
                outline='#FF6600', width=4, fill=''
            )
            # Add label positioned away from click area
            canvas.create_text(x, y-35, text="OK", fill='#FF6600', font=('Arial', 12, 'bold'))
        
        # Show the window
        root.deiconify()
        root.update()
        
        # Auto-hide after duration
        def cleanup():
            time_module.sleep(duration)
            try:
                root.destroy()
            except:
                pass
        
        threading.Thread(target=cleanup, daemon=True).start()
        
        # Start the window's event loop in this thread
        try:
            root.mainloop()
        except:
            pass
    
    # Run in separate thread to avoid blocking
    threading.Thread(target=create_and_show, daemon=True).start()


def show_found_locations_debug(search_region, locations, labels=None, colors=None, duration=3, button_sizes=None):
    """
    REUSABLE: Show debug visualization for any found image locations.
    
    Args:
        search_region: (left, top, right, bottom) search area to highlight
        locations: List of (x, y) coordinates where images were found
        labels: List of text labels for each location (optional)
        colors: List of colors for each location (optional, defaults to green variants)
        duration: How long to show visualization (seconds)
        button_sizes: List of (width, height) for each location (optional, defaults to 60x25)
    """
    import tkinter as tk
    import threading
    import time as time_module
    
    # Default values
    if not locations:
        locations = []
    if labels and len(labels) != len(locations):
        labels = [f"Found #{i+1}" for i in range(len(locations))]
    if not labels:
        labels = [f"Found #{i+1}" for i in range(len(locations))]
    if not colors:
        # Default to green for all locations
        colors = ['#00FF00' for _ in locations]
    if not button_sizes:
        button_sizes = [(60, 25) for _ in locations]  # Default button size
    
    def create_and_show():
        # Create a temporary transparent window
        root = tk.Tk()
        root.withdraw()  # Hide initially
        
        # Make it fullscreen and completely transparent
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.attributes('-alpha', 1.0)  # Fully opaque for the shapes
        root.overrideredirect(True)
        
        # Make the window background transparent
        try:
            root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        # Create transparent canvas with black background (which becomes transparent)
        canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw search region rectangle (blue)
        canvas.create_rectangle(
            search_region[0], search_region[1], search_region[2], search_region[3],
            outline='#0066FF', width=3, fill=''
        )
        
        # Draw found locations
        for i, (x, y) in enumerate(locations):
            color = colors[i]
            label = labels[i]
            width, height = button_sizes[i]
            
            # Draw bounding box rectangle
            canvas.create_rectangle(
                x - width//2, y - height//2,
                x + width//2, y + height//2,
                outline=color, width=4, fill=''
            )
            # Add label positioned away from click area
            canvas.create_text(x, y-35, text=label, fill=color, font=('Arial', 12, 'bold'))
        
        # Show the window
        root.deiconify()
        root.update()
        
        # Auto-hide after duration
        def cleanup():
            time_module.sleep(duration)
            try:
                root.destroy()
            except:
                pass
        
        threading.Thread(target=cleanup, daemon=True).start()
        
        # Start the window's event loop in this thread
        try:
            root.mainloop()
        except:
            pass
    
    # Run in separate thread to avoid blocking
    threading.Thread(target=create_and_show, daemon=True).start()


# Legacy function - now uses the reusable one
def _show_button_debug_visualization(search_region, apply_location=None, ok_location=None, duration=3):
    """Show debug visualization for Apply and OK buttons - LEGACY (uses reusable function)"""
    locations = []
    labels = []
    colors = []
    
    if apply_location:
        locations.append(apply_location)
        labels.append("APPLY")
        colors.append('#00FF00')  # Green
    
    if ok_location:
        locations.append(ok_location)
        labels.append("OK")
        colors.append('#FF6600')  # Orange
    
    show_found_locations_debug(search_region, locations, labels, colors, duration)


# TODO: Add to utils/graphics.py - Button-specific visualization function
# This should draw rectangles around button locations instead of circles
# def visualize_button_search(search_region, button_locations, button_labels=None, show_duration=3.0):
#     """
#     Visualize button search results with rectangular boundaries instead of circles
#     - Draws rectangles around button locations (better for rectangular buttons)
#     - Labels positioned outside click areas to avoid interference
#     - Optimized for button automation debugging
#     """
#     pass
    
