"""
Image scanner utilities for finding and locating images on screen
Provides functionality to scan for template images within bounding boxes
and return mouse coordinates for clicking
"""
import os
import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any
import mss
import platform


class ImageScanner:
    """
    A class for scanning and locating images within specified bounding boxes
    """
    
    def __init__(self, images_folder: str = "images"):
        """
        Initialize the ImageScanner
        
        Args:
            images_folder (str): Path to the folder containing template images
        """
        self.images_folder = images_folder
        self.template_cache = {}
        
    def load_template(self, image_name: str) -> Optional[np.ndarray]:
        """
        Load a template image from the images folder
        
        Args:
            image_name (str): Name of the image file
            
        Returns:
            np.ndarray: The loaded template image, or None if not found
        """
        # Check cache first
        if image_name in self.template_cache:
            return self.template_cache[image_name]
            
        # Construct full path
        image_path = os.path.join(self.images_folder, image_name)
        
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Template image not found: {image_path}")
            
        # Load image
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        # Cache the template
        self.template_cache[image_name] = template
        
        return template
    
    def capture_screen_region(self, bounding_box: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Capture a specific region of the screen
        
        Args:
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of the region
            
        Returns:
            np.ndarray: Screenshot of the specified region
        """
        x, y, width, height = bounding_box
        
        with mss.mss() as sct:
            # Define the region to capture
            region = {"top": y, "left": x, "width": width, "height": height}
            
            # Capture the screen region
            screenshot = sct.grab(region)
            
            # Convert to numpy array (BGR format for OpenCV)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
    
    def find_template_in_region(self, 
                               template: np.ndarray, 
                               region_image: np.ndarray,
                               threshold: float = 0.8,
                               method: int = cv2.TM_CCOEFF_NORMED) -> Optional[Tuple[int, int, float]]:
        """
        Find a template image within a region using template matching
        
        Args:
            template (np.ndarray): The template image to search for
            region_image (np.ndarray): The region to search in
            threshold (float): Minimum confidence threshold (0.0 to 1.0)
            method (int): OpenCV template matching method
            
        Returns:
            Tuple[int, int, float]: (x, y, confidence) of the best match, or None if not found
        """
        # Perform template matching
        result = cv2.matchTemplate(region_image, template, method)
        
        # Find the best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # For correlation methods, we want the maximum value
        if method in [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED]:
            confidence = max_val
            match_loc = max_loc
        else:
            confidence = 1.0 - min_val
            match_loc = min_loc
        
        # Check if confidence meets threshold
        if confidence >= threshold:
            return match_loc[0], match_loc[1], confidence
        
        return None
    
    def scan_for_image(self, 
                      image_name: str, 
                      bounding_box: Tuple[int, int, int, int],
                      threshold: float = 0.8,
                      click_offset: Tuple[int, int] = (0, 0)) -> Optional[Tuple[int, int]]:
        """
        Scan for an image within a bounding box and return mouse click coordinates
        
        Args:
            image_name (str): Name of the template image file
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of search area
            threshold (float): Minimum confidence threshold for template matching
            click_offset (Tuple[int, int]): Offset from template center for click position
            
        Returns:
            Tuple[int, int]: (x, y) coordinates for mouse click, or None if not found
        """
        try:
            # Load the template image
            template = self.load_template(image_name)
            
            # Capture the screen region
            region_image = self.capture_screen_region(bounding_box)
            
            # Find the template in the region
            match_result = self.find_template_in_region(template, region_image, threshold)
            
            if match_result is None:
                return None
            
            # Extract match coordinates and confidence
            template_x, template_y, confidence = match_result
            
            # Get template dimensions
            template_height, template_width = template.shape[:2]
            
            # Calculate the center of the matched template
            center_x = template_x + template_width // 2
            center_y = template_y + template_height // 2
            
            # Apply click offset
            click_x = center_x + click_offset[0]
            click_y = center_y + click_offset[1]
            
            # Convert relative coordinates to absolute screen coordinates
            absolute_x = bounding_box[0] + click_x
            absolute_y = bounding_box[1] + click_y
            
            return absolute_x, absolute_y
            
        except Exception as e:
            print(f"Error scanning for image '{image_name}': {str(e)}")
            return None
    
    def scan_for_multiple_images(self, 
                                image_names: list, 
                                bounding_box: Tuple[int, int, int, int],
                                threshold: float = 0.8) -> Dict[str, Tuple[int, int]]:
        """
        Scan for multiple images within a bounding box
        
        Args:
            image_names (list): List of template image file names
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of search area
            threshold (float): Minimum confidence threshold for template matching
            
        Returns:
            Dict[str, Tuple[int, int]]: Dictionary mapping image names to click coordinates
        """
        results = {}
        
        # Capture the screen region once
        region_image = self.capture_screen_region(bounding_box)
        
        for image_name in image_names:
            try:
                # Load the template image
                template = self.load_template(image_name)
                
                # Find the template in the region
                match_result = self.find_template_in_region(template, region_image, threshold)
                
                if match_result is not None:
                    # Extract match coordinates
                    template_x, template_y, confidence = match_result
                    
                    # Get template dimensions
                    template_height, template_width = template.shape[:2]
                    
                    # Calculate the center of the matched template
                    center_x = template_x + template_width // 2
                    center_y = template_y + template_height // 2
                    
                    # Convert to absolute screen coordinates
                    absolute_x = bounding_box[0] + center_x
                    absolute_y = bounding_box[1] + center_y
                    
                    results[image_name] = (absolute_x, absolute_y)
                    
            except Exception as e:
                print(f"Error scanning for image '{image_name}': {str(e)}")
                continue
                
        return results
    
    def get_template_info(self, image_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a template image
        
        Args:
            image_name (str): Name of the template image file
            
        Returns:
            Dict[str, Any]: Information about the template (width, height, channels)
        """
        try:
            template = self.load_template(image_name)
            height, width = template.shape[:2]
            channels = template.shape[2] if len(template.shape) > 2 else 1
            
            return {
                "width": width,
                "height": height,
                "channels": channels,
                "shape": template.shape
            }
        except Exception as e:
            print(f"Error getting template info for '{image_name}': {str(e)}")
            return None
    
    def find_all_templates_in_region(self, 
                                     template: np.ndarray, 
                                     region_image: np.ndarray,
                                     threshold: float = 0.8,
                                     method: int = cv2.TM_CCOEFF_NORMED) -> list:
        """
        Find all occurrences of a template image within a region
        
        Args:
            template (np.ndarray): The template image to search for
            region_image (np.ndarray): The region to search in
            threshold (float): Minimum confidence threshold (0.0 to 1.0)
            method (int): OpenCV template matching method
            
        Returns:
            list: List of tuples (x, y, confidence) for all matches above threshold
        """
        # Perform template matching
        result = cv2.matchTemplate(region_image, template, method)
        
        # Find all locations above threshold
        locations = np.where(result >= threshold)
        matches = []
        
        # Convert locations to list of matches
        for pt in zip(*locations[::-1]):  # Switch x and y coordinates
            confidence = result[pt[1], pt[0]]  # Note: result uses (y, x) indexing
            matches.append((pt[0], pt[1], confidence))
        
        # Remove overlapping matches (non-maximum suppression)
        if matches:
            matches = self._remove_overlapping_matches(matches, template.shape[:2])
        
        return matches
    
    def _remove_overlapping_matches(self, matches: list, template_size: Tuple[int, int]) -> list:
        """
        Remove overlapping matches using simple non-maximum suppression
        
        Args:
            matches (list): List of (x, y, confidence) tuples
            template_size (Tuple[int, int]): (height, width) of template
            
        Returns:
            list: Filtered list of non-overlapping matches
        """
        if not matches:
            return matches
        
        # Sort by confidence (highest first)
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
        
        template_height, template_width = template_size
        filtered_matches = []
        
        for match in matches:
            x, y, confidence = match
            
            # Check if this match overlaps with any already accepted match
            overlaps = False
            for accepted_match in filtered_matches:
                ax, ay, _ = accepted_match
                
                # Check for overlap (if centers are too close)
                center_distance = np.sqrt((x - ax)**2 + (y - ay)**2)
                min_distance = min(template_width, template_height) * 0.5
                
                if center_distance < min_distance:
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_matches.append(match)
        
        return filtered_matches

    def scan_for_all_images(self, 
                           image_name: str, 
                           bounding_box: Tuple[int, int, int, int],
                           threshold: float = 0.8,
                           click_offset: Tuple[int, int] = (0, 0)) -> list:
        """
        Scan for all occurrences of an image within a bounding box
        
        Args:
            image_name (str): Name of the template image file
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of search area
            threshold (float): Minimum confidence threshold for template matching
            click_offset (Tuple[int, int]): Offset from template center for click position
            
        Returns:
            list: List of (x, y) coordinates for all found instances
        """
        try:
            # Load the template image
            template = self.load_template(image_name)
            
            # Capture the screen region
            region_image = self.capture_screen_region(bounding_box)
            
            # Find all templates in the region
            matches = self.find_all_templates_in_region(template, region_image, threshold)
            
            if not matches:
                return []
            
            # Get template dimensions
            template_height, template_width = template.shape[:2]
            
            # Convert matches to absolute coordinates
            absolute_coordinates = []
            for template_x, template_y, confidence in matches:
                # Calculate the center of the matched template
                center_x = template_x + template_width // 2
                center_y = template_y + template_height // 2
                
                # Apply click offset
                click_x = center_x + click_offset[0]
                click_y = center_y + click_offset[1]
                
                # Convert relative coordinates to absolute screen coordinates
                absolute_x = bounding_box[0] + click_x
                absolute_y = bounding_box[1] + click_y
                
                absolute_coordinates.append((absolute_x, absolute_y))
            
            return absolute_coordinates
            
        except Exception as e:
            print(f"Error scanning for all images '{image_name}': {str(e)}")
            return []


# Convenience functions for easy usage
def scan_for_image(image_name: str, 
                  bounding_box: Tuple[int, int, int, int],
                  threshold: float = 0.8,
                  click_offset: Tuple[int, int] = (0, 0),
                  images_folder: str = "images") -> Optional[Tuple[int, int]]:
    """
    Convenience function to scan for a single image
    
    Args:
        image_name (str): Name of the template image file
        bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of search area
        threshold (float): Minimum confidence threshold for template matching
        click_offset (Tuple[int, int]): Offset from template center for click position
        images_folder (str): Path to the folder containing template images
        
    Returns:
        Tuple[int, int]: (x, y) coordinates for mouse click, or None if not found
    """
    scanner = ImageScanner(images_folder)
    return scanner.scan_for_image(image_name, bounding_box, threshold, click_offset)


def scan_for_multiple_images(image_names: list, 
                            bounding_box: Tuple[int, int, int, int],
                            threshold: float = 0.8,
                            images_folder: str = "images") -> Dict[str, Tuple[int, int]]:
    """
    Convenience function to scan for multiple images
    
    Args:
        image_names (list): List of template image file names
        bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of search area
        threshold (float): Minimum confidence threshold for template matching
        images_folder (str): Path to the folder containing template images
        
    Returns:
        Dict[str, Tuple[int, int]]: Dictionary mapping image names to click coordinates
    """
    scanner = ImageScanner(images_folder)
    return scanner.scan_for_multiple_images(image_names, bounding_box, threshold)


def scan_for_all_occurrences(image_name: str, 
                            bounding_box: Tuple[int, int, int, int],
                            threshold: float = 0.8,
                            click_offset: Tuple[int, int] = (0, 0),
                            images_folder: str = "images") -> list:
    """
    Convenience function to scan for all occurrences of a single image
    
    Args:
        image_name (str): Name of the template image file
        bounding_box (Tuple[int, int, int, int]): (x, y, width, height) of search area
        threshold (float): Minimum confidence threshold for template matching
        click_offset (Tuple[int, int]): Offset from template center for click position
        images_folder (str): Path to the folder containing template images
        
    Returns:
        list: List of (x, y) coordinates for all found instances
    """
    scanner = ImageScanner(images_folder)
    return scanner.scan_for_all_images(image_name, bounding_box, threshold, click_offset)


def scan_image_with_bbox(automation_helper, image_name: str = "plus-collapsed.png", 
                        threshold: float = 0.8, images_folder: str = "images", bbox: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
    """
    Scan for image within automation helper's bounding box
    
    Args:
        automation_helper: ManualAutomationHelper instance with bbox
        image_name: Name of the template image file
        threshold: Confidence threshold for matching
        images_folder: Path to images folder
        
    Returns:
        Dict containing scan results and metadata
    """
    try:
        # Get bounding box from automation helper
        if bbox is None:
            if automation_helper is None:
                raise ValueError("automation_helper cannot be None when bbox is not provided")
            bbox = automation_helper.get_bbox()
        left, top, right, bottom = bbox
        
        # Convert bbox from (left, top, right, bottom) to (x, y, width, height)
        bounding_box = (left, top, right - left, bottom - top)
        
        # Perform the scan
        locations = scan_for_all_occurrences(image_name, bounding_box, threshold=threshold, images_folder=images_folder)
        
        # Calculate relative coordinates
        results = []
        for x, y in locations:
            rel_x = x - left
            rel_y = y - top
            results.append({
                'absolute': (x, y),
                'relative': (rel_x, rel_y)
            })
        
        return {
            'success': True,
            'image_name': image_name,
            'threshold': threshold,
            'bbox': bbox,
            'search_area': f"{bounding_box[2]}x{bounding_box[3]} pixels",
            'found_count': len(locations),
            'locations': results
        }
        
    except FileNotFoundError:
        return {
            'success': False,
            'error': f"Template image '{image_name}' not found in images folder."
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"An error occurred while scanning: {str(e)}"
        }


def create_advanced_scan_dialog(parent_window, automation_helper):
    """
    Create advanced image scanning dialog
    
    Args:
        parent_window: Parent tkinter window
        automation_helper: ManualAutomationHelper instance
        
    Returns:
        None (opens dialog window)
    """
    import tkinter as tk
    from tkinter import messagebox
    
    # Create dialog window
    scan_window = tk.Toplevel(parent_window)
    scan_window.title("Advanced Image Scanner")
    scan_window.geometry("450x400")
    scan_window.transient(parent_window)
    scan_window.grab_set()
    
    # Variables
    image_name_var = tk.StringVar(value="plus-collapsed.png")
    threshold_var = tk.DoubleVar(value=0.8)
    use_window_bbox_var = tk.BooleanVar(value=True)
    images_folder_var = tk.StringVar(value="images")
    
    # Main frame
    main_frame = tk.Frame(scan_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Configuration frame
    config_frame = tk.LabelFrame(main_frame, text="Scan Configuration", padx=5, pady=5)
    config_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Image name
    tk.Label(config_frame, text="Image Name:").grid(row=0, column=0, sticky="w", pady=2)
    tk.Entry(config_frame, textvariable=image_name_var, width=25).grid(row=0, column=1, sticky="ew", pady=2)
    
    # Images folder
    tk.Label(config_frame, text="Images Folder:").grid(row=1, column=0, sticky="w", pady=2)
    tk.Entry(config_frame, textvariable=images_folder_var, width=25).grid(row=1, column=1, sticky="ew", pady=2)
    
    # Threshold
    tk.Label(config_frame, text="Confidence Threshold:").grid(row=2, column=0, sticky="w", pady=2)
    threshold_frame = tk.Frame(config_frame)
    threshold_frame.grid(row=2, column=1, sticky="ew", pady=2)
    
    threshold_scale = tk.Scale(threshold_frame, from_=0.1, to=1.0, resolution=0.05, 
                              orient=tk.HORIZONTAL, variable=threshold_var, length=200)
    threshold_scale.pack(side=tk.LEFT)
    
    threshold_label = tk.Label(threshold_frame, text="0.8")
    threshold_label.pack(side=tk.LEFT, padx=(5, 0))
    
    def update_threshold_label(*args):
        threshold_label.config(text=f"{threshold_var.get():.2f}")
    threshold_var.trace('w', update_threshold_label)
    
    # Search area option
    tk.Checkbutton(config_frame, text="Use window bounding box (recommended)", 
                  variable=use_window_bbox_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
    
    config_frame.columnconfigure(1, weight=1)
    
    # Results frame
    results_frame = tk.LabelFrame(main_frame, text="Scan Results", padx=5, pady=5)
    results_frame.pack(fill=tk.BOTH, expand=True)
    
    # Results text area with scrollbar
    text_frame = tk.Frame(results_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    results_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9))
    scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=results_text.yview)
    results_text.configure(yscrollcommand=scrollbar.set)
    
    results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def perform_scan():
        try:
            image_name = image_name_var.get().strip()
            threshold = threshold_var.get()
            use_window_bbox = use_window_bbox_var.get()
            images_folder = images_folder_var.get().strip()
            
            if not image_name:
                results_text.insert(tk.END, "❌ Error: Please enter an image name.\n\n")
                results_text.see(tk.END)
                return
            
            results_text.insert(tk.END, f"🔍 Scanning for '{image_name}' (threshold: {threshold:.2f})...\n")
            
            if use_window_bbox and automation_helper:
                # Use automation helper's bbox
                result = scan_image_with_bbox(automation_helper, image_name, threshold, images_folder)
                
                if result['success']:
                    results_text.insert(tk.END, f"📍 Search area: {result['search_area']} (window bbox)\n")
                    
                    if result['found_count'] > 0:
                        results_text.insert(tk.END, f"✅ Found {result['found_count']} instance(s):\n")
                        for i, location in enumerate(result['locations'], 1):
                            abs_pos = location['absolute']
                            rel_pos = location['relative']
                            results_text.insert(tk.END, f"  {i}. Abs:({abs_pos[0]},{abs_pos[1]}) Rel:({rel_pos[0]},{rel_pos[1]})\n")
                    else:
                        results_text.insert(tk.END, "❌ No instances found.\n")
                else:
                    results_text.insert(tk.END, f"❌ {result['error']}\n")
                    
            else:
                # Use full screen
                import tkinter as temp_tk
                temp_root = temp_tk.Tk()
                temp_root.withdraw()
                screen_width = temp_root.winfo_screenwidth()
                screen_height = temp_root.winfo_screenheight()
                temp_root.destroy()
                
                bounding_box = (0, 0, screen_width, screen_height)
                results_text.insert(tk.END, f"📍 Search area: {screen_width}x{screen_height} pixels (full screen)\n")
                
                locations = scan_for_all_occurrences(image_name, bounding_box, threshold=threshold, images_folder=images_folder)
                
                if locations:
                    results_text.insert(tk.END, f"✅ Found {len(locations)} instance(s):\n")
                    for i, (x, y) in enumerate(locations, 1):
                        results_text.insert(tk.END, f"  {i}. Position: ({x}, {y})\n")
                else:
                    results_text.insert(tk.END, "❌ No instances found.\n")
                    
            results_text.insert(tk.END, "─" * 50 + "\n\n")
            results_text.see(tk.END)
            
        except Exception as e:
            results_text.insert(tk.END, f"❌ Error: {str(e)}\n\n")
            results_text.see(tk.END)
    
    def clear_results():
        results_text.delete(1.0, tk.END)
    
    # Buttons frame
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    tk.Button(button_frame, text="🔍 Scan", command=perform_scan, 
             bg="#4CAF50", fg="white", padx=20).pack(side=tk.LEFT, padx=(0, 5))
    tk.Button(button_frame, text="🗑️ Clear", command=clear_results, 
             bg="#FF9800", fg="white", padx=20).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="❌ Close", command=scan_window.destroy, 
             bg="#f44336", fg="white", padx=20).pack(side=tk.RIGHT)
