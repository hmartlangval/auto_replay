"""
Example demonstrating the TextReader class usage.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from utils
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from utils import TextReader, text_reader

def demo_text_reader():
    """Demonstrate various ways to use the TextReader class."""
    
    print("=== TextReader Demo ===")
    
    # Method 1: Using the convenience instance
    print("\n1. Using convenience instance:")
    print(f"Root directory: {text_reader.root_directory}")
    
    # Method 2: Creating your own instance
    print("\n2. Creating custom instance:")
    reader = TextReader()
    print(f"Root directory: {reader.root_directory}")
    
    # Example usage with real files from the project
    print("\n3. Reading project files:")
    
    # Try to read requirements.txt
    try:
        requirements_content = text_reader.read_file("requirements.txt")
        print(f"Requirements.txt content (first 200 chars):")
        print(requirements_content[:200] + "..." if len(requirements_content) > 200 else requirements_content)
    except Exception as e:
        print(f"Could not read requirements.txt: {e}")
    
    # Check if a file exists
    print(f"\n4. File existence check:")
    print(f"requirements.txt exists: {text_reader.file_exists('requirements.txt')}")
    print(f"non_existent.txt exists: {text_reader.file_exists('non_existent.txt')}")
    
    # Safe reading with default content
    print(f"\n5. Safe reading:")
    safe_content = text_reader.read_file_safe("non_existent.txt", "Default content")
    print(f"Safe read result: {safe_content}")
    
    # Get full path
    print(f"\n6. Full path resolution:")
    full_path = text_reader.get_full_path("requirements.txt")
    print(f"Full path to requirements.txt: {full_path}")
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    demo_text_reader() 