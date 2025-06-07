#!/usr/bin/env python3
"""Test undo functionality with proper timing."""

import tempfile
import time
from pathlib import Path
from src.records import Records
from src.record_serializer import RecordSerializer

with tempfile.TemporaryDirectory() as temp_dir:
    demo_file = Path(temp_dir) / "demo.json"
    
    # Save 1: Amsterdam only
    records1 = Records(demo_file)
    records1.location(name="Amsterdam")
    RecordSerializer.serialize_and_persist(records1._collections, records1._json_path)
    
    time.sleep(0.01)  # Ensure different timestamp
    
    # Save 2: Amsterdam + Berlin + Fight Club
    records1.location(name="Berlin") 
    records1.gym(name="Fight Club")
    RecordSerializer.serialize_and_persist(records1._collections, records1._json_path)
    
    # Before undo: should have 2 locations, 1 gym
    assert len(records1._collections['location']) == 2
    assert len(records1._collections['gym']) == 1
    
    # Undo: removes Save 2, goes back to Save 1
    records1.undo()
    records2 = Records(demo_file)
    
    # After undo: should have 1 location, 0 gyms (Save 1 state)
    assert len(records2._collections.get('location', [])) == 1, f"Expected 1 location, got {len(records2._collections.get('location', []))}"
    assert len(records2._collections.get('gym', [])) == 0, f"Expected 0 gyms, got {len(records2._collections.get('gym', []))}"
    assert records2._collections['location'][0].name == "Amsterdam"
    
print("✓ Undo works - restored to previous save state")
