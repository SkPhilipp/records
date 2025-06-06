"""
RecordSerializer - Handles type validation and serialization for Records.
"""

import json
from typing import Any, Dict, List
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
    def serialize_and_persist(collections: Dict[str, List['Record']], file_path: Path) -> None:
        """Convert collections to serializable format and persist to file."""
        data = {}
        for collection_name, records_list in collections.items():
            data[collection_name] = [record.to_dict() for record in records_list]
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_and_deserialize(file_path: Path, records_class, records_manager) -> Dict[str, List['Record']]:
        """Load data from file and convert back to Record objects."""
        if not file_path.exists():
            return {}
        
        with open(file_path, 'r') as f:
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
