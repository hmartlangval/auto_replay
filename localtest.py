import os
from utils.windows_automation import ManualAutomationHelper
from utils.image_scanner import scan_for_all_occurrences
from utils.graphics import ScreenOverlay, visualize_image_search
import time
from dotenv import load_dotenv
load_dotenv()

# Debug visualization flag - set to True to see search regions and found locations
DEBUG_VISUALIZATION = False
LOCAL_DEV = os.getenv("LOCAL_DEV", "False") == "True"


def collapse_tree_items(automation_helper=None):
    """
    Collapse all tree items by clicking minus-expanded.png images from bottom to top.
    Searches only in the top-left 30% of the window's bounding box.
    """
    
    if automation_helper is None and not LOCAL_DEV:
        raise ValueError("automation_helper is required when not in local development mode")
    
    # Get the window's bounding box
    if LOCAL_DEV:
        bbox = (100, 100, 1050, 646)
    else:
        bbox = automation_helper.get_bbox()
    left, top, right, bottom = bbox
    
    # Calculate the top-left 30% region
    search_width = int((right - left) * 0.3)  # 30% of width
    search_height = int((bottom - top) * 0.5)  # 50% of height
    search_region = (left, top, left + search_width, top + search_height)
    
    print(f"📐 Window bbox: {bbox}")
    print(f"🔍 Search region (top-left 30%): {search_region}")
    
    graphics.draw_rectangle(search_region[0], search_region[1], search_region[2], search_region[3], color="#00FF00", width=3, label="Search Region")
    
    max_iterations = 20  # Safety limit to prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}: Searching for expanded tree items...")
        
        # Visualize the search region (only if debug enabled)
        visualize_image_search(
            search_region=search_region,
            region_label=f"Tree Search Region (Iteration {iteration})",
            show_duration=2.0,
            enabled=DEBUG_VISUALIZATION
        )
        
        # Search for all minus-expanded.png images in the search region
        results = scan_for_all_occurrences(
            image_name="minus-expanded.png",
            bounding_box=search_region,
            threshold=0.8
        )
        
        if not results or len(results) == 0:
            print("✅ No more expanded tree items found. Collapse complete!")
            # Show final visualization with no matches
            visualize_image_search(
                search_region=search_region,
                found_locations=[],
                region_label="Final Search - No Matches",
                show_duration=3.0,
                enabled=DEBUG_VISUALIZATION
            )
            break
        
        print(f"📍 Found {len(results)} expanded tree items")
        
        # Show visualization with found locations
        visualize_image_search(
            search_region=search_region,
            found_locations=results,
            region_label=f"Found {len(results)} Tree Items",
            show_duration=3.0,
            enabled=DEBUG_VISUALIZATION
        )
        
        # Sort results by Y coordinate (bottom to top)
        # results format: [(x, y), ...]
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        
        # Click the bottommost expanded item
        center_x, center_y = sorted_results[0]
        print(f"🖱️  Clicking bottommost expanded item at ({center_x}, {center_y})")
        
        # Click the minus icon to collapse
        success = automation_helper.click((center_x, center_y))
        if not success:
            print(f"❌ Failed to click at ({center_x}, {center_y})")
            break
        
        # Wait for the UI to update
        time.sleep(0.5)
        
        # Optional: Verify the click worked by checking if the item is still there
        # This helps ensure we're making progress
        verification_results = scan_for_all_occurrences(
            image_name="minus-expanded.png",
            bounding_box=search_region,
            threshold=0.8
        )
        
        if verification_results and len(verification_results) >= len(results):
            print("⚠️  Warning: No change detected after click, continuing anyway...")
        else:
            print(f"✅ Progress made: {len(results)} → {len(verification_results) if verification_results else 0} expanded items")
    
    if iteration >= max_iterations:
        print(f"⚠️  Reached maximum iterations ({max_iterations}). Stopping to prevent infinite loop.")
    
    print("🎉 Tree collapse process completed!")



def setup_project_window():
    # Initialize window handle
    project_setup_window_handle = ManualAutomationHelper(target_window_title="Project Settings", title_starts_with=True)
    print(f"✅ Found Project Setup window: {project_setup_window_handle.hwnd}")

    # Check if window was found
    if not project_setup_window_handle.hwnd:
        print("❌ No Project Setup window found")
        return False

    # Reposition the window to the desired location
    project_setup_window_handle.setup_window(bbox=(100, 100, 1050, 646))
       
    return project_setup_window_handle


def explore_tree_items(automation_helper):
    """
    Explore the tree items by clicking the plus-collapsed.png images from top to bottom.
    Searches only in the top-left 30% of the window's bounding box.
    """
    # First step is to collapse all tree items
    print("🔍 Starting tree collapse process...")
    collapse_tree_items(automation_helper)
    
    time.sleep(1)
    print("🔍 Starting tree exploration process...")
    
    # Second step is to expand the first parent node
    # search for plus-collapsed.png image in the top-left 30% of the window's bounding box.
    plus_results = scan_for_all_occurrences("plus-collapsed.png", automation_helper.get_bbox(), threshold=0.8)
    # if plus_results:
    #     automation_helper.click(plus_results[0])  # Click the first plus icon found
    
    # Now i want to click on the text to the right of the plus-collapsed.png image and focus on that
    # automation_helper.click((plus_results[0][0] + 40, plus_results[0][1]))
    # graphics.draw_rectangle(plus_results[0][0] + 30, plus_results[0][1]-10, plus_results[0][0] + 40, plus_results[0][1]+5, color="#00FF00", width=2, label="Focus Region")
    
    
    
    


graphics = ScreenOverlay()

if __name__ == "__main__":
    graphics.create_overlay()  # Create the overlay window
    
    if LOCAL_DEV:
        graphics.draw_rectangle(100, 100, 1050, 646, color="#00FF00", width=3, label="Main Region")
        # Draw small squares inside the main rectangle (x1, y1, x2, y2)
        graphics.draw_rectangle(110, 110, 130, 130, color="#FF0000", width=2, label="Square 1")  # 20x20 square
        graphics.draw_rectangle(110, 140, 130, 160, color="#FF0000", width=2, label="Square 2")  # 20x20 square  
        graphics.draw_rectangle(110, 170, 130, 190, color="#FF0000", width=2, label="Square 3")  # 20x20 square
        graphics.draw_rectangle(110, 200, 130, 220, color="#FF0000", width=2, label="Square 4")  # 20x20 square
        graphics.show_overlay()    # Make it visible
    else:
        project_setup_window_handle = setup_project_window()
        explore_tree_items(project_setup_window_handle)
    
    time.sleep(2)
    graphics.destroy_overlay()