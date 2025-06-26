"""
TreeView Path Computer - Pure logic for computing navigation key sequences
Separation of concerns: Path computation vs UI automation
"""

class TreeviewPathComputer:
    """
    Computes optimal key sequences for treeview navigation.
    Pure logic class with no UI dependencies.
    """
    
    def compute_navigation_path(self, current_path: str, target_path: str) -> list:
        """
        Compute the key sequence needed to navigate from current to target.
        
        Args:
            current_path: Current position (e.g., "1.2.3")
            target_path: Target position (e.g., "1.4.1")
            
        Returns:
            List of keys: ["Left", "Down", "Down", "Right", "Down"]
        """
        if current_path == target_path:
            return []  # Already at target
        
        key_sequence = []
        self._navigate_recursive(current_path, target_path, key_sequence)
        return key_sequence
    
    def _navigate_recursive(self, current: str, target: str, keys: list) -> bool:
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
                # Identical paths
                return True
            elif len(current_parts) < len(target_parts):
                # Current is shorter - expand further
                # e.g., current="1.2", target="1.2.3"
                remaining_target = '.'.join(target_parts[len(current_parts):])
                return self._expand_to_target(remaining_target, keys)
            else:
                # Current is longer - collapse and check again
                # e.g., current="1.2.3", target="1.2"
                new_current = '.'.join(current_parts[:-1])
                keys.append("Left")
                return self._navigate_recursive(new_current, target, keys)
        
        # Mismatch found at index
        current_at_mismatch = int(current_parts[mismatch_index])
        target_at_mismatch = int(target_parts[mismatch_index])
        
        # Check if both are at last parts (siblings)
        current_at_last = (mismatch_index == len(current_parts) - 1)
        target_at_last = (mismatch_index == len(target_parts) - 1)
        
        if current_at_last and target_at_last:
            # Both at last parts - sibling navigation
            return self._navigate_siblings(current_at_mismatch, target_at_mismatch, keys)
        
        elif current_at_last and not target_at_last:
            # Current at last, target has more - sibling move then expand
            # e.g., current="1.2", target="1.3.4"
            if not self._navigate_siblings(current_at_mismatch, target_at_mismatch, keys):
                return False
            
            # Now at target's parent level, expand further
            remaining_target = '.'.join(target_parts[mismatch_index + 1:])
            return self._expand_to_target(remaining_target, keys)
        
        elif not current_at_last and target_at_last:
            # Current has more, target at last - collapse and check again
            # e.g., current="1.2.3", target="1.4"
            new_current = '.'.join(current_parts[:-1])
            keys.append("Left")
            return self._navigate_recursive(new_current, target, keys)
        
        else:
            # Both have more parts - cross parent navigation
            # e.g., current="1.2.3", target="1.4.5"
            new_current = '.'.join(current_parts[:-1])
            keys.append("Left")
            return self._navigate_recursive(new_current, target, keys)
    
    def _navigate_siblings(self, current_pos: int, target_pos: int, keys: list) -> bool:
        """Add sibling navigation keys to the sequence"""
        moves = target_pos - current_pos
        
        if moves > 0:
            for _ in range(moves):
                keys.append("Down")
        elif moves < 0:
            for _ in range(abs(moves)):
                keys.append("Up")
        
        return True
    
    def _expand_to_target(self, remaining_path: str, keys: list) -> bool:
        """Add expansion keys to reach remaining target path"""
        parts = remaining_path.split('.')
        
        for part in parts:
            keys.append("Right")  # Expand
            target_pos = int(part)
            
            # Navigate to position
            for _ in range(target_pos):
                keys.append("Down")
        
        return True


# Example usage and testing
if __name__ == "__main__":
    computer = TreeviewPathComputer()
    
    test_cases = [
        ("1", "1.1.1"),       # Root to deep child
        ("1.1.1", "1.1.2"),   # Sibling navigation
        ("1.1.2", "1.3.1"),   # Cross-parent navigation
        ("1.3.1", "1.2"),     # Deep to shallow
        ("1.2", "1.2.3"),     # Expand further
        ("1.2.3", "1.2"),     # Collapse back
        ("1", "2"),           # Root sibling
    ]
    
    print("🧮 TreeView Path Computer Test")
    print("=" * 40)
    
    for current, target in test_cases:
        keys = computer.compute_navigation_path(current, target)
        print(f"{current} → {target}: {keys}") 