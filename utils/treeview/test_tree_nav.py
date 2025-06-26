"""
Test TreeView Navigation Logic
Simple left-to-right comparison approach without actual key integration
"""

class MockTreeNavigator:
    def __init__(self):
        self.current_path = "1"
        self.key_sequence = []
    
    def log_key(self, key):
        """Log a key press without actually sending it"""
        self.key_sequence.append(key)
        print(f"  → {key}")
    
    def navigate_to_path(self, target_path):
        """Navigate using simple left-to-right comparison logic"""
        print(f"\nNavigating from {self.current_path} to {target_path}")
        self.key_sequence.clear()
        
        if self.current_path == target_path:
            print("✅ Already at target")
            return True
        
        success = self._navigate_recursive(self.current_path, target_path)
        
        if success:
            self.current_path = target_path
            print(f"✅ Navigation complete. Keys: {' '.join(self.key_sequence)}")
        else:
            print("❌ Navigation failed")
        
        return success
    
    def _navigate_recursive(self, current, target):
        """Recursive navigation using left-to-right comparison"""
        current_parts = current.split('.')
        target_parts = target.split('.')
        
        # Find first mismatch
        mismatch_index = None
        for i in range(min(len(current_parts), len(target_parts))):
            if current_parts[i] != target_parts[i]:
                mismatch_index = i
                break
        
        # No mismatch found - one path is prefix of another
        if mismatch_index is None:
            if len(current_parts) == len(target_parts):
                # Identical paths (shouldn't happen due to early check)
                return True
            elif len(current_parts) < len(target_parts):
                # Current is shorter - expand further
                # e.g., current="1.2", target="1.2.3"
                remaining_target = '.'.join(target_parts[len(current_parts):])
                return self._expand_to_target(remaining_target)
            else:
                # Current is longer - collapse and check again
                # e.g., current="1.2.3", target="1.2"
                new_current = '.'.join(current_parts[:-1])
                self.log_key("Left")
                return self._navigate_recursive(new_current, target)
        
        # Mismatch found at index
        current_at_mismatch = int(current_parts[mismatch_index])
        target_at_mismatch = int(target_parts[mismatch_index])
        
        # Check if both are at last parts (siblings)
        current_at_last = (mismatch_index == len(current_parts) - 1)
        target_at_last = (mismatch_index == len(target_parts) - 1)
        
        if current_at_last and target_at_last:
            # Both at last parts - sibling navigation
            return self._navigate_siblings(current_at_mismatch, target_at_mismatch)
        
        elif current_at_last and not target_at_last:
            # Current at last, target has more - sibling move then expand
            # e.g., current="1.2", target="1.3.4"
            if not self._navigate_siblings(current_at_mismatch, target_at_mismatch):
                return False
            
            # Now at target's parent level, expand further
            remaining_target = '.'.join(target_parts[mismatch_index + 1:])
            return self._expand_to_target(remaining_target)
        
        elif not current_at_last and target_at_last:
            # Current has more, target at last - collapse and check again
            # e.g., current="1.2.3", target="1.4"
            new_current = '.'.join(current_parts[:-1])
            self.log_key("Left")
            return self._navigate_recursive(new_current, target)
        
        else:
            # Both have more parts - cross parent navigation
            # e.g., current="1.2.3", target="1.4.5"
            new_current = '.'.join(current_parts[:-1])
            self.log_key("Left")
            return self._navigate_recursive(new_current, target)
    
    def _navigate_siblings(self, current_pos, target_pos):
        """Navigate between siblings at same level"""
        moves = target_pos - current_pos
        
        if moves > 0:
            for _ in range(moves):
                self.log_key("Down")
        elif moves < 0:
            for _ in range(abs(moves)):
                self.log_key("Up")
        
        return True
    
    def _expand_to_target(self, remaining_path):
        """Expand down to remaining target path"""
        parts = remaining_path.split('.')
        
        for part in parts:
            self.log_key("Right")  # Expand
            target_pos = int(part)
            
            # Navigate to position
            for _ in range(target_pos):
                self.log_key("Down")
        
        return True


def test_navigation():
    """Test various navigation scenarios"""
    nav = MockTreeNavigator()
    
    test_cases = [
        ("1", "1.1.1"),       # Root to deep child
        ("1.1.1", "1.1.2"),   # Sibling navigation
        ("1.1.2", "1.3.1"),   # Cross-parent navigation
        ("1.3.1", "1.2"),     # Deep to shallow
        ("1.2", "1.2.3"),     # Expand further
        ("1.2.3", "1.2"),     # Collapse back
        ("1", "2"),           # Root sibling
    ]
    
    for current, target in test_cases:
        nav.current_path = current
        nav.navigate_to_path(target)
        print()


if __name__ == "__main__":
    print("🧪 TreeView Navigation Logic Test")
    print("=" * 40)
    test_navigation() 