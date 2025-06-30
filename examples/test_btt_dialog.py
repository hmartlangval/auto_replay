#!/usr/bin/env python3
"""
Test script for BTT Selection Dialog
Tests the dialog functionality without running full automation
"""

import sys
import os

# Add the automation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'automation', 'btt'))

from btt import BTTSelectionDialog

def test_dialog():
    """Test the BTT selection dialog"""
    print("🧪 Testing BTT Selection Dialog...")
    print("=" * 50)
    
    # Create and show dialog
    dialog = BTTSelectionDialog()
    config = dialog.show()
    
    if config is None:
        print("❌ Dialog was cancelled")
        return False
    
    print("✅ Dialog completed successfully!")
    print(f"📊 Results:")
    print(f"   Test Type: {config['test_type']}")
    print(f"   Use Custom: {config['use_custom']}")
    print(f"   Test Type Prompt: {len(config['test_type_prompt'])} characters")
    print(f"   Custom Prompt: {len(config['custom_prompt'])} characters")
    
    print("\n📄 Test Type Prompt Content:")
    print("-" * 30)
    print(config['test_type_prompt'])
    
    if config['custom_prompt']:
        print("\n🔧 Custom Prompt Content:")
        print("-" * 30)
        print(config['custom_prompt'])
    
    print("\n🎯 Combined Configuration:")
    print("-" * 30)
    combined = config['test_type_prompt']
    if config['custom_prompt']:
        combined += '\n' + config['custom_prompt']
    print(combined)
    
    return True

if __name__ == "__main__":
    try:
        success = test_dialog()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()