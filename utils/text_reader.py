import os
import sys
from pathlib import Path
from typing import Optional


class TextReader:
    """
    A text reader class that reads text files relative to the application root directory.
    Handles both development environment and packaged executable scenarios.
    """
    
    def __init__(self):
        self._root_dir = self._get_application_root()
    
    def _get_application_root(self) -> Path:
        """
        Determine the application root directory.
        Works for both development and packaged executable scenarios.
        """
        if getattr(sys, 'frozen', False):
            # Running as packaged executable
            # sys.executable points to the exe file
            return Path(sys.executable).parent
        else:
            # Running in development
            # Go up from utils directory to project root
            return Path(__file__).parent.parent
    
    def read_file(self, relative_path: str) -> str:
        """
        Read a text file given its path relative to the application root.
        
        Args:
            relative_path: Path relative to application root (e.g., "automation/btt/one.txt")
            
        Returns:
            Content of the file as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        # Normalize the path (handle forward/backward slashes)
        normalized_path = Path(relative_path)
        full_path = self._root_dir / normalized_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {full_path}")
        except Exception as e:
            raise IOError(f"Error reading file {full_path}: {str(e)}")
    
    def read_file_safe(self, relative_path: str, default_content: str = "") -> str:
        """
        Read a text file safely, returning default content if file doesn't exist or can't be read.
        
        Args:
            relative_path: Path relative to application root
            default_content: Content to return if file can't be read
            
        Returns:
            Content of the file as a string, or default_content if error occurs
        """
        try:
            return self.read_file(relative_path)
        except (FileNotFoundError, IOError):
            return default_content
    
    def file_exists(self, relative_path: str) -> bool:
        """
        Check if a file exists relative to the application root.
        
        Args:
            relative_path: Path relative to application root
            
        Returns:
            True if file exists, False otherwise
        """
        normalized_path = Path(relative_path)
        full_path = self._root_dir / normalized_path
        return full_path.exists() and full_path.is_file()
    
    def get_full_path(self, relative_path: str) -> Path:
        """
        Get the full absolute path for a relative path.
        
        Args:
            relative_path: Path relative to application root
            
        Returns:
            Full absolute path as Path object
        """
        normalized_path = Path(relative_path)
        return self._root_dir / normalized_path
    
    @property
    def root_directory(self) -> Path:
        """Get the application root directory."""
        return self._root_dir


# Convenience instance for easy importing
text_reader = TextReader() 