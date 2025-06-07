"""
RecordSerializer - Handles type validation and serialization for Records.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class RecordSerializer:
    """Handles type validation and serialization for Records."""
    
    @staticmethod
    def is_supported_value(value: Any) -> bool:
        """Check if a value is supported (recursively for lists and dicts)."""
        if value is None:
            return True
        
        # Basic supported types
        if isinstance(value, (bool, int, float, str)):
            return True
        
        # Lists - all elements must be supported
        if isinstance(value, list):
            return all(RecordSerializer.is_supported_value(item) for item in value)
        
        # Dicts - all values must be supported, keys must be strings
        if isinstance(value, dict):
            return (all(isinstance(key, str) for key in value.keys()) and
                    all(RecordSerializer.is_supported_value(val) for val in value.values()))
        
        return False
    
    @staticmethod
    def validate_value(value: Any, attribute_name: str, collection_name: str) -> None:
        """Validate that a value is supported. Raises TypeError if not."""
        if not RecordSerializer.is_supported_value(value):
            raise TypeError(
                f"Attribute '{attribute_name}' in collection '{collection_name}' "
                f"must be JSON-native (bool, int, float, str, list, dict), got {type(value).__name__}"
            )
    
    @staticmethod
    def _ensure_records_dir(records_dir: Path) -> None:
        """Ensure the .records directory exists."""
        records_dir.mkdir(exist_ok=True)
    
    @staticmethod
    def _get_timestamped_filename() -> str:
        """Generate a timestamped filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # microseconds to milliseconds
        return f"{timestamp}.json"
    
    @staticmethod
    def _get_most_recent_file(records_dir: Path) -> Optional[Path]:
        """Get the most recent records file from the .records directory."""
        if not records_dir.exists():
            return None
        
        json_files = list(records_dir.glob("*.json"))
        if not json_files:
            return None
        
        # Sort by filename (timestamp) in descending order
        json_files.sort(key=lambda x: x.name, reverse=True)
        return json_files[0]
    
    @staticmethod
    def serialize_and_persist(collections: Dict[str, List['Record']], base_path: Path) -> None:
        """Convert collections to serializable format and persist to timestamped file."""
        records_dir = base_path.parent / ".records"
        RecordSerializer._ensure_records_dir(records_dir)
        
        filename = RecordSerializer._get_timestamped_filename()
        file_path = records_dir / filename
        
        data = {}
        for collection_name, records_list in collections.items():
            data[collection_name] = [record.to_dict() for record in records_list]
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_and_deserialize(base_path: Path, records_class, records_manager) -> Dict[str, List['Record']]:
        """Load data from the most recent file and convert back to Record objects."""
        records_dir = base_path.parent / ".records"
        most_recent_file = RecordSerializer._get_most_recent_file(records_dir)
        
        if not most_recent_file:
            return {}
        
        with open(most_recent_file, 'r') as f:
            data = json.load(f)
        
        collections = {}
        for collection_name, records_data in data.items():
            collections[collection_name] = []
            for record_data in records_data:
                # Create a new record instance
                record_id = record_data.get('id', 0)
                
                # Remove id from kwargs since it will be set by the Record constructor
                kwargs = {k: v for k, v in record_data.items() if k != 'id'}
                
                # Create the record
                record = records_class(collection_name, records_manager, **kwargs)
                
                # Override the ID to match the loaded data
                record._id = record_id
                
                collections[collection_name].append(record)
        
        return collections
    
    @staticmethod
    def undo(base_path: Path) -> bool:
        """Remove the most recent records file to undo changes. Returns True if successful."""
        records_dir = base_path.parent / ".records"
        most_recent_file = RecordSerializer._get_most_recent_file(records_dir)
        
        if not most_recent_file:
            return False
        
        try:
            most_recent_file.unlink()
            return True
        except OSError:
            return False
