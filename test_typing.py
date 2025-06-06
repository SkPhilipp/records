"""
Test script to demonstrate type enforcement in Records.
"""

import tempfile
from pathlib import Path
from records import Records

def test_type_enforcement():
    print("Testing type enforcement...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        records = Records(Path(temp_dir) / "typing_test.json")
        
        # Create a location with initial types
        loc = records.location(lat=12.345, long=67.890)
        print(f"Created location: lat={loc.lat} (type: {type(loc.lat).__name__})")
        
        # This should work - same type
        try:
            loc.lat = 52.370
            print(f"✓ Setting lat to another float: {loc.lat}")
        except TypeError as e:
            print(f"✗ Unexpected error: {e}")
        
        # This should work - None is always allowed
        try:
            loc.lat = None
            print(f"✓ Setting lat to None: {loc.lat}")
        except TypeError as e:
            print(f"✗ Unexpected error: {e}")
        
        # This should fail - wrong type
        try:
            loc.lat = "not a number"
            print(f"✗ This shouldn't happen: {loc.lat}")
        except TypeError as e:
            print(f"✓ Correctly rejected string for float: {e}")
        
        # Test with a new attribute (should work with any type initially)
        try:
            loc.name = "Amsterdam"
            print(f"✓ New attribute 'name' set to string: {loc.name}")
        except TypeError as e:
            print(f"✗ Unexpected error for new attribute: {e}")
        
        # Now that 'name' is established as string, try to set it to int
        try:
            loc.name = 123
            print(f"✗ This shouldn't happen: {loc.name}")
        except TypeError as e:
            print(f"✓ Correctly rejected int for string: {e}")
        
        # But None should still work
        try:
            loc.name = None
            print(f"✓ Setting name to None: {loc.name}")
        except TypeError as e:
            print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_type_enforcement() 