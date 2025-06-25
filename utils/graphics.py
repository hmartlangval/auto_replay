"""
Graphics Utility for Visual Debugging
Provides functions to draw visual indicators on screen for debugging image search regions
"""

import tkinter as tk
from typing import Tuple, Optional, List
import time
import threading


class ScreenOverlay:
    """A transparent overlay window for drawing visual indicators on screen"""
    
    def __init__(self):
        self.root = None
        self.canvas = None
        self.overlay_items = []
        self.is_visible = False
    
    def create_overlay(self):
        """Create the transparent overlay window"""
        if self.root is not None:
            return  # Already created
        
        self.root = tk.Tk()
        self.root.title("Debug Overlay")
        
        # Make window fullscreen and transparent
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.7)  # Semi-transparent
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Make the window click-through (Windows specific)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except tk.TclError:
            pass  # Not supported on all platforms
        
        # Create canvas that fills the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(
            self.root,
            width=screen_width,
            height=screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind escape key to close overlay
        self.root.bind('<Escape>', lambda e: self.hide_overlay())
        self.root.focus_set()
        
        # Update the display to make sure window appears
        self.root.update()
        
        self.is_visible = True
    
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, 
                      color: str = "#00FF00", width: int = 3, 
                      label: str = None) -> int:
        """
        Draw a rectangle on the overlay
        
        Args:
            x1, y1: Top-left corner coordinates
            x2, y2: Bottom-right corner coordinates
            color: Border color (default: bright green)
            width: Border width in pixels
            label: Optional text label for the rectangle
            
        Returns:
            int: Item ID for the drawn rectangle
        """
        if not self.is_visible:
            self.create_overlay()
        
        # Draw rectangle border
        rect_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color,
            width=width,
            fill=""  # Transparent fill
        )
        
        # Add label if provided
        label_id = None
        if label:
            # Position label at top-left of rectangle
            label_id = self.canvas.create_text(
                x1 + 5, y1 + 5,
                text=label,
                fill=color,
                font=("Arial", 12, "bold"),
                anchor="nw"
            )
        
        # Store item info
        item_info = {
            'type': 'rectangle',
            'rect_id': rect_id,
            'label_id': label_id,
            'coords': (x1, y1, x2, y2),
            'color': color,
            'label': label
        }
        self.overlay_items.append(item_info)
        
        # Update the display to show the drawn rectangle
        if self.root:
            self.root.update()
        
        return rect_id
    
    def draw_point(self, x: int, y: int, color: str = "#FF0000", 
                   size: int = 10, label: str = None) -> int:
        """
        Draw a point (small circle) on the overlay
        
        Args:
            x, y: Point coordinates
            color: Point color (default: bright red)
            size: Point size in pixels
            label: Optional text label for the point
            
        Returns:
            int: Item ID for the drawn point
        """
        if not self.is_visible:
            self.create_overlay()
        
        # Draw circle
        half_size = size // 2
        circle_id = self.canvas.create_oval(
            x - half_size, y - half_size,
            x + half_size, y + half_size,
            outline=color,
            fill=color,
            width=2
        )
        
        # Add label if provided
        label_id = None
        if label:
            label_id = self.canvas.create_text(
                x + half_size + 5, y,
                text=label,
                fill=color,
                font=("Arial", 10, "bold"),
                anchor="w"
            )
        
        # Store item info
        item_info = {
            'type': 'point',
            'circle_id': circle_id,
            'label_id': label_id,
            'coords': (x, y),
            'color': color,
            'label': label
        }
        self.overlay_items.append(item_info)
        
        return circle_id
    
    def clear_overlay(self):
        """Clear all drawn items from the overlay"""
        if self.canvas:
            self.canvas.delete("all")
        self.overlay_items.clear()
    
    def hide_overlay(self):
        """Hide the overlay window"""
        if self.root:
            self.root.withdraw()
            self.is_visible = False
    
    def show_overlay(self):
        """Show the overlay window"""
        if self.root:
            self.root.deiconify()
            self.root.update()  # Force display update
            self.is_visible = True
        else:
            self.create_overlay()
    
    def destroy_overlay(self):
        """Destroy the overlay window completely"""
        if self.root:
            self.root.destroy()
            self.root = None
            self.canvas = None
            self.overlay_items.clear()
            self.is_visible = False
    
    def auto_hide_after(self, seconds: float):
        """Automatically hide the overlay after specified seconds"""
        def hide_delayed():
            time.sleep(seconds)
            if self.is_visible:
                self.hide_overlay()
        
        threading.Thread(target=hide_delayed, daemon=True).start()


# Global overlay instance
_global_overlay = None

def get_overlay() -> ScreenOverlay:
    """Get the global overlay instance"""
    global _global_overlay
    if _global_overlay is None:
        _global_overlay = ScreenOverlay()
    return _global_overlay


# Convenience functions
def draw_search_region(x1: int, y1: int, x2: int, y2: int, 
                      label: str = "Search Region", 
                      color: str = "#00FF00", 
                      width: int = 3,
                      auto_hide_seconds: float = 5.0,
                      enabled: bool = False) -> int:
    """
    Draw a search region rectangle with bright green border
    
    Args:
        x1, y1: Top-left corner coordinates
        x2, y2: Bottom-right corner coordinates
        label: Text label for the region
        color: Border color (default: bright green)
        width: Border width
        auto_hide_seconds: Automatically hide after this many seconds (0 = no auto-hide)
        enabled: Whether to show the visualization (default: False)
        
    Returns:
        int: Item ID for the drawn rectangle (or 0 if disabled)
    """
    if not enabled:
        print(f"🔍 Debug: Search region {label} at ({x1}, {y1}) to ({x2}, {y2})")
        return 0
    
    overlay = get_overlay()
    rect_id = overlay.draw_rectangle(x1, y1, x2, y2, color, width, label)
    
    if auto_hide_seconds > 0:
        overlay.auto_hide_after(auto_hide_seconds)
    
    return rect_id


def draw_found_locations(locations: List[Tuple[int, int]], 
                        color: str = "#FF0000",
                        size: int = 12,
                        auto_hide_seconds: float = 5.0,
                        enabled: bool = False) -> List[int]:
    """
    Draw points at found image locations
    
    Args:
        locations: List of (x, y) coordinates
        color: Point color (default: bright red)
        size: Point size
        auto_hide_seconds: Automatically hide after this many seconds (0 = no auto-hide)
        enabled: Whether to show the visualization (default: False)
        
    Returns:
        List[int]: Item IDs for the drawn points (or empty list if disabled)
    """
    if not enabled:
        print(f"🎯 Debug: Found {len(locations)} locations: {locations}")
        return []
    
    overlay = get_overlay()
    point_ids = []
    
    for i, (x, y) in enumerate(locations, 1):
        label = f"Found #{i}"
        point_id = overlay.draw_point(x, y, color, size, label)
        point_ids.append(point_id)
    
    if auto_hide_seconds > 0:
        overlay.auto_hide_after(auto_hide_seconds)
    
    return point_ids


def visualize_image_search(search_region: Tuple[int, int, int, int],
                          found_locations: List[Tuple[int, int]] = None,
                          region_label: str = "Image Search Region",
                          show_duration: float = 5.0,
                          enabled: bool = False):
    """
    Visualize an image search operation by showing the search region and found locations
    
    Args:
        search_region: (x1, y1, x2, y2) coordinates of search region
        found_locations: List of (x, y) coordinates where images were found
        region_label: Label for the search region
        show_duration: How long to show the visualization (seconds)
        enabled: Whether to show the visualization (default: False to avoid interfering with image search)
    """
    if not enabled:
        # Just print debug info without showing overlay
        if found_locations:
            print(f"🎯 Debug: {len(found_locations)} matches found in search region {search_region}")
        else:
            print(f"🔍 Debug: Searching in region {search_region} (no matches)")
        return
    
    overlay = get_overlay()
    
    # Clear any existing overlays
    overlay.clear_overlay()
    
    # Draw search region
    x1, y1, x2, y2 = search_region
    overlay.draw_rectangle(x1, y1, x2, y2, "#00FF00", 3, region_label)
    
    # Draw found locations if provided
    if found_locations:
        for i, (x, y) in enumerate(found_locations, 1):
            overlay.draw_point(x, y, "#FF0000", 12, f"Match #{i}")
        
        print(f"🎯 Visualizing: {len(found_locations)} matches found in search region")
    else:
        print("🔍 Visualizing: Search region only (no matches)")
    
    # Show the overlay
    overlay.show_overlay()
    
    # Auto-hide after duration
    if show_duration > 0:
        overlay.auto_hide_after(show_duration)
    
    print(f"👁️  Visual overlay displayed for {show_duration} seconds (Press ESC to close early)")


def clear_all_overlays():
    """Clear all visual overlays"""
    overlay = get_overlay()
    overlay.clear_overlay()


def hide_overlays():
    """Hide all visual overlays"""
    overlay = get_overlay()
    overlay.hide_overlay()


def show_overlays():
    """Show visual overlays"""
    overlay = get_overlay()
    overlay.show_overlay()


def destroy_overlays():
    """Destroy all visual overlays completely"""
    global _global_overlay
    if _global_overlay:
        _global_overlay.destroy_overlay()
        _global_overlay = None


# Example usage and testing
if __name__ == "__main__":
    print("🎨 Testing Graphics Overlay...")
    
    # Test 1: Draw a search region
    print("\n1. Drawing search region...")
    draw_search_region(100, 100, 400, 300, "Test Search Region", auto_hide_seconds=3)
    
    time.sleep(4)  # Wait for auto-hide
    
    # Test 2: Draw multiple found locations
    print("\n2. Drawing found locations...")
    test_locations = [(150, 150), (250, 200), (350, 250)]
    draw_found_locations(test_locations, auto_hide_seconds=3)
    
    time.sleep(4)  # Wait for auto-hide
    
    # Test 3: Full visualization
    print("\n3. Full image search visualization...")
    search_region = (50, 50, 500, 400)
    found_locations = [(100, 100), (200, 150), (300, 200), (400, 300)]
    
    visualize_image_search(
        search_region=search_region,
        found_locations=found_locations,
        region_label="Complete Search Demo",
        show_duration=5
    )
    
    print("\n✅ Graphics overlay test completed!")
    print("💡 Use visualize_image_search() in your image scanning code for debugging")
