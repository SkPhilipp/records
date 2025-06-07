"""
Test JSON-native type enforcement.
"""

import tempfile
from pathlib import Path
from datetime import datetime
from src.records import Records


class CustomObject:
    pass


def test_json_types():
    print("Testing JSON-native type enforcement...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        records = Records(Path(temp_dir) / "json_test.json")
        
        # Test all JSON-native types
        try:
            record = records.test_record(
                string_val="hello",
                int_val=42,
                float_val=3.14,
                bool_val=True,
                list_val=[1, 2, "three"],
                dict_val={"key": "value", "number": 123},
                nested={"level1": {"level2": [1, 2, {"level3": "deep"}]}}
            )
            print("✓ All JSON-native types accepted")
        except TypeError as e:
            print(f"✗ Unexpected error with JSON-native types: {e}")
        
        # Test nested JSON structures
        try:
            record.nested = {
                "level1": {
                    "level2": [1, 2, {"level3": "deep"}]
                }
            }
            print("✓ Nested JSON structures accepted")
        except TypeError as e:
            print(f"✗ Unexpected error with nested JSON: {e}")
        
        # Test invalid types
        test_cases = [
            ("datetime", datetime.now()),
            ("set", {1, 2, 3}),
            ("tuple", (1, 2, 3)),
            ("custom_object", CustomObject()),
        ]
        
        for type_name, invalid_value in test_cases:
            try:
                setattr(record, "invalid", invalid_value)
                print(f"✗ {type_name} incorrectly accepted")
            except TypeError as e:
                print(f"✓ {type_name} correctly rejected: {e}")
        
        # Test dict with non-string keys
        try:
            record.bad_dict = {1: "invalid key"}
            print("✗ Dict with non-string key incorrectly accepted")
        except TypeError as e:
            print(f"✓ Dict with non-string key correctly rejected: {e}")
        
        # Test list with invalid content
        try:
            record.bad_list = [1, 2, datetime.now()]
            print("✗ List with invalid content incorrectly accepted")
        except TypeError as e:
            print(f"✓ List with invalid content correctly rejected: {e}")


if __name__ == "__main__":
    test_json_types()
