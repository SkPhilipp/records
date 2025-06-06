"""
Demo test showing Records functionality with locations and gyms.
"""

import tempfile
from pathlib import Path
from records import Records

def test_records_demo():
    """Test basic Records functionality with the original demo scenario."""
    with tempfile.TemporaryDirectory() as temp_dir:
        records = Records(Path(temp_dir) / "demo.json")
        
        # Create a location record as shown in README
        loc = records.location(lat=12.345, long=67.890)
        
        # Add address information
        loc.address = "123 Main St, Amsterdam, Netherlands"
        
        # Create another location
        loc2 = records.location(lat=52.370, long=4.895)
        loc2.address = "Dam Square, Amsterdam, Netherlands"
        loc2.name = "Amsterdam Center"
        
        # Create some gym records for the boxing gym example
        records.gym(name="Fight Club Amsterdam", location="Amsterdam", travel_time=25)
        records.gym(name="Boxing Gym Central", location="Amsterdam", travel_time=35)
        records.gym(name="Heavy Bag Training", location="Amsterdam", travel_time=15)
        
        # Filter gyms by travel time (example of data manipulation)
        all_gyms = records.gym.all()
        nearby_gyms = [gym for gym in all_gyms if gym.get('travel_time', 0) <= 30]
        
        # Delete a gym
        records.gym.delete(1)

if __name__ == "__main__":
    test_records_demo()
