"""
File utilities for sequence recorder
Handles filename generation and file operations
"""
import os
import sys


def get_app_data_path(relative_path):
    """Get path for runtime data (sequences, prompts, images) - always relative to .exe location"""
    if getattr(sys, 'frozen', False):
        # Running as .exe - use directory where .exe is located
        app_dir = os.path.dirname(sys.executable)
    else:
        # Development mode - use current directory
        app_dir = os.path.abspath(".")
    
    return os.path.join(app_dir, relative_path)


def generate_unique_filename(base_name, sequences_dir_name="sequences"):
    """Generate a unique filename by adding numbers if file exists"""
    # Use proper path handling for .exe compatibility
    sequences_dir = get_app_data_path(sequences_dir_name)
    
    clean_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '_', '-')).strip()
    clean_name = clean_name.replace(' ', '_').lower()
    
    base_filename = os.path.join(sequences_dir, f"{clean_name}.py")
    
    if not os.path.exists(base_filename):
        return base_filename, clean_name
    
    # File exists, find the next available number
    counter = 2
    while True:
        numbered_name = f"{clean_name}_{counter}"
        numbered_filename = os.path.join(sequences_dir, f"{numbered_name}.py")
        if not os.path.exists(numbered_filename):
            return numbered_filename, numbered_name
        counter += 1


def generate_suggested_name(sequences_dir_name="sequences"):
    """Generate a unique suggested name for the sequence"""
    # Use proper path handling for .exe compatibility
    sequences_dir = get_app_data_path(sequences_dir_name)
    
    if not os.path.exists(sequences_dir):
        return "my_sequence"
    
    base_name = "my_sequence"
    base_filename = os.path.join(sequences_dir, f"{base_name}.py")
    
    if not os.path.exists(base_filename):
        return base_name
    
    # File exists, find the next available number
    counter = 2
    while True:
        numbered_name = f"{base_name}_{counter}"
        numbered_filename = os.path.join(sequences_dir, f"{numbered_name}.py")
        if not os.path.exists(numbered_filename):
            return numbered_name
        counter += 1


def ensure_sequences_directory(sequences_dir_name="sequences"):
    """Ensure the sequences directory exists"""
    # Use proper path handling for .exe compatibility
    sequences_dir = get_app_data_path(sequences_dir_name)
    
    if not os.path.exists(sequences_dir):
        os.makedirs(sequences_dir)
    return sequences_dir 