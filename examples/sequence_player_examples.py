"""
Example: How to use the Sequence Player utility from anywhere
This demonstrates various ways to execute recorded sequences
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from utils
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import the sequence player utilities
from utils import (
    play_sequence, play_sequence_async, play_sequence_with_delay,
    list_available_sequences, sequence_exists, SequencePlayer
)

def main():
    print("🎬 Sequence Player Examples")
    print("=" * 50)
    
    # 1. List all available sequences
    print("\n1. Available sequences:")
    sequences = list_available_sequences()
    for seq in sequences:
        print(f"   - {seq}")
    
    if not sequences:
        print("   No sequences found!")
        return
    
    # 2. Check if a specific sequence exists
    test_sequence = "my_sequence_2"
    print(f"\n2. Checking if '{test_sequence}' exists:")
    if sequence_exists(test_sequence):
        print(f"   ✅ '{test_sequence}' exists")
    else:
        print(f"   ❌ '{test_sequence}' not found")
        test_sequence = sequences[0]  # Use first available sequence
        print(f"   Using '{test_sequence}' instead")
    
    # 3. Play a sequence synchronously (blocking)
    print(f"\n3. Playing '{test_sequence}' synchronously...")
    success = play_sequence(test_sequence, blocking=True)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # 4. Play a sequence asynchronously (non-blocking)
    print(f"\n4. Playing '{test_sequence}' asynchronously...")
    
    def on_complete(seq_name):
        print(f"   🎉 Async sequence '{seq_name}' completed!")
    
    def on_error(error_msg):
        print(f"   💥 Async sequence failed: {error_msg}")
    
    success = play_sequence_async(test_sequence, on_complete=on_complete, on_error=on_error)
    print(f"   Started: {'✅ Yes' if success else '❌ No'}")
    
    # Wait a bit for async sequence to complete
    import time
    time.sleep(3)
    
    # 5. Play a sequence with delay
    print(f"\n5. Playing '{test_sequence}' with 2-second delay...")
    success = play_sequence_with_delay(test_sequence, delay_seconds=2, blocking=True)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # 6. Using the SequencePlayer class directly for more control
    print(f"\n6. Using SequencePlayer class directly...")
    player = SequencePlayer()
    
    # Custom callbacks
    def detailed_success(seq_name):
        print(f"   🎯 Custom callback: '{seq_name}' finished executing")
    
    def detailed_error(error_msg):
        print(f"   🚨 Custom error handler: {error_msg}")
    
    success = player.play_sequence(
        test_sequence, 
        blocking=False,  # Run in background
        on_complete=detailed_success,
        on_error=detailed_error
    )
    print(f"   Background execution started: {'✅ Yes' if success else '❌ No'}")
    
    # Wait for background execution
    time.sleep(3)
    
    print("\n🎉 All examples completed!")


def example_in_automation_workflow():
    """Example of how to integrate sequence playing in an automation workflow"""
    print("\n" + "=" * 50)
    print("🔧 Integration Example: Automation Workflow")
    print("=" * 50)
    
    # Step 1: Do some automation setup
    print("1. Setting up automation...")
    
    # Step 2: Run a sequence for data entry
    print("2. Running data entry sequence...")
    if play_sequence("my_sequence_2", blocking=True):
        print("   ✅ Data entry completed")
    else:
        print("   ❌ Data entry failed")
        return False
    
    # Step 3: Continue with more automation
    print("3. Continuing with post-sequence automation...")
    
    # Step 4: Run another sequence asynchronously while doing other work
    print("4. Starting background sequence...")
    play_sequence_async("my_sequence_3", 
                       on_complete=lambda seq: print(f"   ✅ Background sequence '{seq}' done"))
    
    # Do other work while sequence runs in background
    print("5. Doing other work while sequence runs...")
    import time
    time.sleep(2)
    
    print("6. Workflow completed!")
    return True


def example_custom_sequences_directory():
    """Example of using a custom sequences directory"""
    print("\n" + "=" * 50)
    print("🗂️  Custom Directory Example")
    print("=" * 50)
    
    # You can specify a custom sequences directory
    try:
        # This would use a different directory if it existed
        custom_player = SequencePlayer(sequences_dir="custom_sequences")
        sequences = custom_player.list_sequences()
        print(f"Custom sequences found: {sequences}")
    except FileNotFoundError:
        print("Custom sequences directory not found (this is expected)")
    
    # Using default directory
    default_player = SequencePlayer()  # Uses default 'sequences' folder
    sequences = default_player.list_sequences()
    print(f"Default sequences: {sequences}")


if __name__ == "__main__":
    # Run the main examples
    main()
    
    # Show integration example
    example_in_automation_workflow()
    
    # Show custom directory example
    example_custom_sequences_directory() 