"""
File utilities for sequence recorder
Handles filename generation and file operations
"""
import os


def generate_unique_filename(base_name, sequences_dir="sequences"):
    """Generate a unique filename by adding numbers if file exists"""
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


def generate_suggested_name(sequences_dir="sequences"):
    """Generate a unique suggested name for the sequence"""
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


def ensure_sequences_directory(sequences_dir="sequences"):
    """Ensure the sequences directory exists"""
    if not os.path.exists(sequences_dir):
        os.makedirs(sequences_dir)
    return sequences_dir 