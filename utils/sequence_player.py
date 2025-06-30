"""
Sequence Player Utility
Provides easy methods to execute recorded sequences from anywhere in the codebase.
"""

import os
import sys
import importlib.util
import threading
import time
from typing import Optional, Callable
from pathlib import Path


class SequencePlayer:
    """Utility class for playing recorded sequences"""
    
    def __init__(self, sequences_dir: str = None):
        """
        Initialize the sequence player.
        
        Args:
            sequences_dir: Path to sequences directory. If None, uses default 'sequences' folder.
        """
        if sequences_dir is None:
            # Default to sequences folder in project root
            project_root = Path(__file__).parent.parent
            self.sequences_dir = project_root / "sequences"
        else:
            self.sequences_dir = Path(sequences_dir)
        
        if not self.sequences_dir.exists():
            raise FileNotFoundError(f"Sequences directory not found: {self.sequences_dir}")
    
    def list_sequences(self) -> list:
        """
        List all available sequence files.
        
        Returns:
            list: List of sequence names (without .py extension)
        """
        sequences = []
        for file in self.sequences_dir.glob("*.py"):
            if not file.name.startswith("__"):  # Skip __init__.py and similar
                sequences.append(file.stem)
        return sorted(sequences)
    
    def sequence_exists(self, sequence_name: str) -> bool:
        """
        Check if a sequence file exists.
        
        Args:
            sequence_name: Name of the sequence (without .py extension)
            
        Returns:
            bool: True if sequence exists
        """
        sequence_file = self.sequences_dir / f"{sequence_name}.py"
        return sequence_file.exists()
    
    def play_sequence(self, sequence_name: str, blocking: bool = True, 
                     on_complete: Optional[Callable] = None, 
                     on_error: Optional[Callable] = None,
                     **kwargs) -> bool:
        """
        Execute a recorded sequence.
        
        Args:
            sequence_name: Name of the sequence file (without .py extension)
            blocking: If True, waits for sequence to complete. If False, runs in background.
            on_complete: Optional callback function called when sequence completes successfully
            on_error: Optional callback function called if sequence fails
            
        Returns:
            bool: True if sequence started successfully (for non-blocking) or completed successfully (for blocking)
        """
        if not self.sequence_exists(sequence_name):
            error_msg = f"Sequence not found: {sequence_name}"
            print(f"❌ {error_msg}")
            if on_error:
                on_error(error_msg)
            return False
        
        if blocking:
            return self._execute_sequence(sequence_name, on_complete, on_error, **kwargs)
        else:
            # Run in background thread
            thread = threading.Thread(
                target=self._execute_sequence,
                args=(sequence_name, on_complete, on_error),
                kwargs=kwargs,
                daemon=True
            )
            thread.start()
            return True
    
    def _execute_sequence(self, sequence_name: str, 
                         on_complete: Optional[Callable] = None,
                         on_error: Optional[Callable] = None,
                         **kwargs) -> bool:
        """
        Internal method to execute a sequence.
        
        Args:
            sequence_name: Name of the sequence
            on_complete: Callback for successful completion
            on_error: Callback for errors
            
        Returns:
            bool: True if successful
        """
        try:
            print(f"🎬 Starting sequence: {sequence_name}")
            
            # Load the sequence module dynamically
            sequence_file = self.sequences_dir / f"{sequence_name}.py"
            spec = importlib.util.spec_from_file_location(sequence_name, sequence_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load sequence module: {sequence_name}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for the replay function - it should be named replay_{sequence_name}
            replay_function_name = f"replay_{sequence_name}"
            if not hasattr(module, replay_function_name):
                raise AttributeError(f"Replay function not found: {replay_function_name}")
            
            replay_function = getattr(module, replay_function_name)
            
            # Execute the sequence
            success = replay_function(**kwargs)
            
            if success:
                print(f"✅ Sequence completed successfully: {sequence_name}")
                if on_complete:
                    on_complete(sequence_name)
                return True
            else:
                error_msg = f"Sequence failed: {sequence_name}"
                print(f"❌ {error_msg}")
                if on_error:
                    on_error(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error executing sequence '{sequence_name}': {str(e)}"
            print(f"❌ {error_msg}")
            if on_error:
                on_error(error_msg)
            return False
    
    def play_sequence_with_delay(self, sequence_name: str, delay_seconds: float = 0, 
                                blocking: bool = True, on_complete: Optional[Callable] = None,
                                on_error: Optional[Callable] = None,
                                **kwargs) -> bool:
        """
        Execute a sequence after a specified delay.
        
        Args:
            sequence_name: Name of the sequence
            delay_seconds: Delay before starting sequence
            blocking: Whether to wait for completion
            on_complete: Callback for successful completion
            on_error: Callback for errors
            
        Returns:
            bool: True if started successfully
        """
        def delayed_execution():
            if delay_seconds > 0:
                print(f"⏳ Waiting {delay_seconds}s before starting sequence: {sequence_name}")
                time.sleep(delay_seconds)
            return self._execute_sequence(sequence_name, on_complete, on_error, **kwargs)
        
        if blocking:
            return delayed_execution()
        else:
            thread = threading.Thread(target=delayed_execution, daemon=True)
            thread.start()
            return True


# Global instance for easy access
_global_player = None

def get_sequence_player(sequences_dir: str = None) -> SequencePlayer:
    """
    Get the global sequence player instance.
    
    Args:
        sequences_dir: Optional custom sequences directory
        
    Returns:
        SequencePlayer: The global player instance
    """
    global _global_player
    if _global_player is None or sequences_dir is not None:
        _global_player = SequencePlayer(sequences_dir)
    return _global_player


# Convenience functions for easy usage
def play_sequence(sequence_name: str, blocking: bool = True, 
                 on_complete: Optional[Callable] = None,
                 on_error: Optional[Callable] = None,
                 **kwargs) -> bool:
    """
    Play a sequence using the global player.
    
    Args:
        sequence_name: Name of sequence to play
        blocking: Whether to wait for completion
        on_complete: Callback for successful completion
        on_error: Callback for errors
        
    Returns:
        bool: Success status
    """
    player = get_sequence_player()
    return player.play_sequence(sequence_name, blocking, on_complete, on_error, **kwargs)


def play_sequence_async(sequence_name: str, on_complete: Optional[Callable] = None,
                       on_error: Optional[Callable] = None) -> bool:
    """
    Play a sequence asynchronously (non-blocking).
    
    Args:
        sequence_name: Name of sequence to play
        on_complete: Callback for successful completion
        on_error: Callback for errors
        
    Returns:
        bool: True if started successfully
    """
    return play_sequence(sequence_name, blocking=False, on_complete=on_complete, on_error=on_error)


def play_sequence_with_delay(sequence_name: str, delay_seconds: float, 
                           blocking: bool = True, on_complete: Optional[Callable] = None,
                           on_error: Optional[Callable] = None) -> bool:
    """
    Play a sequence after a delay.
    
    Args:
        sequence_name: Name of sequence to play
        delay_seconds: Delay before starting
        blocking: Whether to wait for completion
        on_complete: Callback for successful completion
        on_error: Callback for errors
        
    Returns:
        bool: Success status
    """
    player = get_sequence_player()
    return player.play_sequence_with_delay(sequence_name, delay_seconds, blocking, on_complete, on_error)


def list_available_sequences() -> list:
    """
    Get list of all available sequences.
    
    Returns:
        list: List of sequence names
    """
    player = get_sequence_player()
    return player.list_sequences()


def sequence_exists(sequence_name: str) -> bool:
    """
    Check if a sequence exists.
    
    Args:
        sequence_name: Name of sequence to check
        
    Returns:
        bool: True if sequence exists
    """
    player = get_sequence_player()
    return player.sequence_exists(sequence_name)


# Example usage and testing
if __name__ == "__main__":
    # Test the utility
    player = SequencePlayer()
    
    print("Available sequences:")
    sequences = player.list_sequences()
    for seq in sequences:
        print(f"  - {seq}")
    
    # Example of playing a sequence
    if sequences:
        test_sequence = sequences[0]
        print(f"\nTesting sequence: {test_sequence}")
        
        def on_success(seq_name):
            print(f"🎉 Callback: Sequence '{seq_name}' completed successfully!")
        
        def on_failure(error_msg):
            print(f"💥 Callback: Sequence failed - {error_msg}")
        
        # Play with callbacks
        success = player.play_sequence(test_sequence, blocking=True, 
                                     on_complete=on_success, on_error=on_failure)
        print(f"Final result: {success}") 