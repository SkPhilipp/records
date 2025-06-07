"""
Test undo functionality for Records.
"""

import tempfile
import time
from pathlib import Path
from src.records import Records
from src.record_serializer import RecordSerializer


def test_undo_restores_previous_state():
    """Test that undo restores data to the previous saved state."""
    print("Testing undo restores previous state...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        demo_file = Path(temp_dir) / "test_records.json"
        
        # Save 1: Amsterdam only
        records1 = Records(demo_file)
        records1.location(name="Amsterdam")
        RecordSerializer.serialize_and_persist(records1._collections, records1._json_path)
        
        time.sleep(0.01)  # Ensure different timestamp
        
        # Save 2: Amsterdam + Berlin + Fight Club
        records1.location(name="Berlin") 
        records1.gym(name="Fight Club")
        RecordSerializer.serialize_and_persist(records1._collections, records1._json_path)
        
        # Verify current state
        assert len(records1._collections['location']) == 2
        assert len(records1._collections['gym']) == 1
        
        # Undo and reload
        records1.undo()
        records2 = Records(demo_file)
        
        # Should be back to Save 1 state
        assert len(records2._collections.get('location', [])) == 1
        assert len(records2._collections.get('gym', [])) == 0
        assert records2._collections['location'][0].name == "Amsterdam"
    
    print("✓ Undo restores previous state correctly")


def test_undo_with_no_saves():
    """Test undo behavior when no save files exist."""
    print("Testing undo with no saves...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        demo_file = Path(temp_dir) / "test_records.json"
        records = Records(demo_file)
        
        # Try undo without any saves (should just print message)
        records.undo()
    
    print("✓ Undo with no saves handled correctly")


if __name__ == "__main__":
    test_undo_restores_previous_state()
    test_undo_with_no_saves()
    print("\nAll undo functionality tests passed! ✅")
