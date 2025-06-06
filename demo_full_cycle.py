"""
Simple demo showing Records save/load cycle with basic filtering.
"""

import tempfile
from pathlib import Path
from records import Records
from record_serializer import RecordSerializer


def demo_save_load_cycle():
    """Demo showing complete save/load cycle with filtering."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = Path(temp_dir) / "demo_data.json"
        
        print("=== Part 1: Creating and saving data ===")
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
        
        print(f"Created {records.location.count()} locations")
        print(f"Created {records.gym.count()} gyms")
        print(f"Data saved to {data_file}")
        
        print("\n=== Part 2: Loading and filtering data ===")
        
        # Load data in a fresh Records instance
        records = Records(data_file)
        
        print(f"Loaded {records.location.count()} locations")
        print(f"Loaded {records.gym.count()} gyms")
        
        # Filter gyms by travel time
        all_gyms = records.gym.all()
        nearby_gyms = [gym for gym in all_gyms if gym.get('travel_time', 0) <= 30]
        
        print(f"\nNearby gyms (≤30 min):")
        for gym in nearby_gyms:
            print(f"  • {gym['name']}: {gym['travel_time']} min")
        
        # Delete a gym and show results
        records.gym.delete(1)
        print(f"\nAfter deletion: {records.gym.count()} gyms remaining")
        
        print("Demo completed (temp file auto-cleaned)")


if __name__ == "__main__":
    demo_save_load_cycle() 