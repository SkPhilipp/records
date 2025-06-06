"""
Test the complete save and load cycle for Records persistence.
"""

import json
import tempfile
from pathlib import Path
from src.records import Records, Record
from src.record_serializer import RecordSerializer


def test_save_load_cycle():
    """Test that data persists correctly through save and load cycle."""
    print("Testing save and load cycle...")
    
    # Use temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test_records.json"
        
        # Create first Records instance and add some data
        records1 = Records(test_file)
        records1._collections.clear()  # Clear any existing data
        records1._next_ids.clear()  # Reset ID counters
    
        # Create some test records
        location1 = records1.location(lat=52.37, long=4.895, name="Amsterdam", country="Netherlands")
        location2 = records1.location(lat=40.7128, long=-74.0060, name="New York", country="USA")
        gym1 = records1.gym(name="Amsterdam Boxing", location="Amsterdam", rating=4.5)
        gym2 = records1.gym(name="NYC Fitness", location="New York", rating=4.8)
        
        print(f"Created {len(records1._collections['location'])} locations and {len(records1._collections['gym'])} gyms")
        
        # Save data manually
        RecordSerializer.serialize_and_persist(records1._collections, records1._json_path)
        
        # Verify file was created and has content
        assert test_file.exists(), "Save file should exist"
        with open(test_file, 'r') as f:
            saved_data = json.load(f)
        
        assert 'location' in saved_data, "Location collection should be saved"
        assert 'gym' in saved_data, "Gym collection should be saved"
        assert len(saved_data['location']) == 2, "Should have 2 locations"
        assert len(saved_data['gym']) == 2, "Should have 2 gyms"
        
        print("✓ Data saved successfully")
        
        # Create new Records instance (simulating restart)
        records2 = Records(test_file)
        
        # Manually load data (simulating what happens in __init__)
        loaded_collections = RecordSerializer.load_and_deserialize(records2._json_path, Record, records2)
        if loaded_collections:
            records2._collections = loaded_collections
            # Update next IDs
            for collection_name, records_list in records2._collections.items():
                if records_list:
                    max_id = max(record._id for record in records_list)
                    records2._next_ids[collection_name] = max_id + 1
        
        print(f"Loaded {len(records2._collections.get('location', []))} locations and {len(records2._collections.get('gym', []))} gyms")
        
        # Verify loaded data matches original
        assert len(records2._collections['location']) == 2, "Should load 2 locations"
        assert len(records2._collections['gym']) == 2, "Should load 2 gyms"
        
        # Check specific data
        locations = records2._collections['location']
        gyms = records2._collections['gym']
        
        # Find Amsterdam location
        amsterdam = next((loc for loc in locations if loc.name == "Amsterdam"), None)
        assert amsterdam is not None, "Amsterdam location should exist"
        assert amsterdam.lat == 52.37, "Amsterdam lat should match"
        assert amsterdam.long == 4.895, "Amsterdam long should match"
        assert amsterdam.country == "Netherlands", "Amsterdam country should match"
        
        # Find NYC location
        nyc = next((loc for loc in locations if loc.name == "New York"), None)
        assert nyc is not None, "New York location should exist"
        assert nyc.lat == 40.7128, "NYC lat should match"
        assert nyc.long == -74.0060, "NYC long should match"
        
        # Check gyms
        amsterdam_gym = next((gym for gym in gyms if gym.name == "Amsterdam Boxing"), None)
        assert amsterdam_gym is not None, "Amsterdam Boxing should exist"
        assert amsterdam_gym.rating == 4.5, "Amsterdam Boxing rating should match"
        
        nyc_gym = next((gym for gym in gyms if gym.name == "NYC Fitness"), None)
        assert nyc_gym is not None, "NYC Fitness should exist"
        assert nyc_gym.rating == 4.8, "NYC Fitness rating should match"
        
        print("✓ All loaded data matches original")
        
        # Test ID continuation - create new records should have correct IDs
        new_location = records2.location(lat=51.5074, long=-0.1278, name="London", country="UK")
        new_gym = records2.gym(name="London Gym", location="London", rating=4.3)
        
        # IDs should continue from where they left off
        assert new_location._id == 2, f"New location ID should be 2, got {new_location._id}"
        assert new_gym._id == 2, f"New gym ID should be 2, got {new_gym._id}"
        
        print("✓ ID continuation works correctly")
        
        # temp_dir cleanup is automatic
        
    print("✓ Save and load cycle test passed!")


def test_empty_file_handling():
    """Test that empty/missing files are handled correctly."""
    print("Testing empty file handling...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with non-existent file
        test_file = Path(temp_dir) / "nonexistent.json"
        
        records = Records(test_file)
        
        # Should handle missing file gracefully
        loaded_collections = RecordSerializer.load_and_deserialize(records._json_path, Record, records)
        assert loaded_collections == {}, "Missing file should return empty dict"
        
        print("✓ Missing file handled correctly")
        
        # Test with empty file
        test_file.write_text("{}")
        loaded_collections = RecordSerializer.load_and_deserialize(records._json_path, Record, records)
        assert loaded_collections == {}, "Empty file should return empty dict"
        
        print("✓ Empty file handled correctly")
        
        # temp_dir cleanup is automatic


if __name__ == "__main__":
    test_save_load_cycle()
    test_empty_file_handling()
    print("\nAll save/load cycle tests passed! ✅")
