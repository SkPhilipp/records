"""
Test showing Records save/load cycle with basic filtering.
"""

import tempfile
from pathlib import Path
from src.records import Records
from src.record_serializer import RecordSerializer


def test_full_save_load_cycle():
    """Test complete save/load cycle with filtering."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = Path(temp_dir) / "demo_data.json"
        
        # Part 1: Creating and saving data
        records = Records(data_file)
        
        # Create location records
        loc = records.location(lat=12.345, long=67.890)
        loc.address = "123 Main St, Amsterdam, Netherlands"
        
        loc2 = records.location(lat=52.370, long=4.895)
        loc2.address = "Dam Square, Amsterdam, Netherlands"
        loc2.name = "Amsterdam Center"
        
        # Create gym records
        records.gym(name="Fight Club Amsterdam", location="Amsterdam", travel_time=25)
        records.gym(name="Boxing Gym Central", location="Amsterdam", travel_time=35)
        records.gym(name="Heavy Bag Training", location="Amsterdam", travel_time=15)
        
        # Save data
        RecordSerializer.serialize_and_persist(records._collections, records._json_path)
        
        assert records.location.count() == 2
        assert records.gym.count() == 3
        
        # Part 2: Loading and filtering data
        
        # Load data in a fresh Records instance
        records = Records(data_file)
        
        assert records.location.count() == 2
        assert records.gym.count() == 3
        
        # Filter gyms by travel time
        all_gyms = records.gym.all()
        nearby_gyms = [gym for gym in all_gyms if gym.get('travel_time', 0) <= 30]
        
        assert len(nearby_gyms) == 2  # Fight Club Amsterdam (25) and Heavy Bag Training (15)
        nearby_names = [gym['name'] for gym in nearby_gyms]
        assert "Fight Club Amsterdam" in nearby_names
        assert "Heavy Bag Training" in nearby_names
        assert "Boxing Gym Central" not in nearby_names  # 35 min, not ≤30
        
        # Delete a gym and verify
        deleted = records.gym.delete(1)  # Boxing Gym Central
        assert deleted == True
        assert records.gym.count() == 2
        
        print("✅ Full cycle test passed!")


if __name__ == "__main__":
    test_full_save_load_cycle()
