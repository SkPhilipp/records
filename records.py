"""
Records - A Python package for managing small amounts of data for AI Agents.

Provides data integrity, consistency, and change tracking with an intuitive interface.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
import atexit


class RecordTypeStructure:
    """Manages structure and type enforcement for a specific record type."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.attributes: Dict[str, Type] = {'id': int}
        self.structure_changes: List[Dict[str, Any]] = []
    
    def add_attribute(self, name: str, value: Any) -> bool:
        """Add a new attribute to the structure. Returns True if it's a new attribute."""
        attr_type = type(value)
        if name not in self.attributes:
            self.attributes[name] = attr_type
            self.structure_changes.append({
                'action': 'add',
                'collection': self.collection_name,
                'attribute': name,
                'type': attr_type.__name__
            })
            return True
        return False
    
    def enforce_type(self, name: str, value: Any) -> None:
        """Enforce type for an existing attribute. Raises TypeError if invalid."""
        if value is None:
            return  # None is always allowed
        
        if name in self.attributes:
            expected_type = self.attributes[name]
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Attribute '{name}' in collection '{self.collection_name}' "
                    f"expects type {expected_type.__name__}, got {type(value).__name__}"
                )
    
    def get_structure_changes(self) -> List[Dict[str, Any]]:
        """Get all structure changes for this record type."""
        return self.structure_changes.copy()
    
    def to_dict(self) -> Dict[str, str]:
        """Return the structure as a dictionary of attribute names to type names."""
        return {name: attr_type.__name__ for name, attr_type in self.attributes.items()}


class Record:
    """Represents a single record in a collection."""
    
    def __init__(self, collection_name: str, records_manager: 'Records', **kwargs):
        self._collection_name = collection_name
        self._records_manager = records_manager
        self._id = records_manager._get_next_id(collection_name)
        
        # Set attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Add to collection
        records_manager._add_record(collection_name, self)
        
        # Track content change
        records_manager._track_content_change('add', collection_name, self._id, kwargs)
    
    def __setattr__(self, name: str, value: Any):
        # Handle internal attributes normally
        if name in ('_records_manager', '_collection_name'):
            super().__setattr__(name, value)
            return
        
        # Get or create the structure for this collection
        structure = self._records_manager._get_structure(self._collection_name)
        
        # Enforce type if it exists
        structure.enforce_type(name, value)
        
        old_value = getattr(self, name, None) if hasattr(self, name) else None
        super().__setattr__(name, value)
        
        # Track structure change
        structure.add_attribute(name, value)
        
        # Track content change
        if old_value != value:
            self._records_manager._track_content_change(
                'update', self._collection_name, self._id, {name: {'old': old_value, 'new': value}}
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        result = {'id': self._id}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result


class Collection:
    """Represents a collection of records."""
    
    def __init__(self, name: str, records_manager: 'Records'):
        self.name = name
        self._records_manager = records_manager
    
    def all(self) -> List[Dict[str, Any]]:
        """Return all records in this collection."""
        return [record.to_dict() for record in self._records_manager._collections.get(self.name, [])]
    
    def get(self, id: int) -> Optional[Record]:
        """Get a record by ID."""
        for record in self._records_manager._collections.get(self.name, []):
            if record._id == id:
                return record
        return None
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        collection = self._records_manager._collections.get(self.name, [])
        for i, record in enumerate(collection):
            if record._id == id:
                deleted_record = collection.pop(i)
                self._records_manager._track_content_change('delete', self.name, id, deleted_record.to_dict())
                return True
        return False
    
    def count(self) -> int:
        """Return the number of records in this collection."""
        return len(self._records_manager._collections.get(self.name, []))


class Records:
    """Main interface for managing structured data collections."""
    
    def __init__(self):
        self._collections: Dict[str, List[Record]] = {}
        self._next_ids: Dict[str, int] = {}
        self._structures: Dict[str, RecordTypeStructure] = {}
        self._content_changes: List[Dict[str, Any]] = []
        self._db_path = Path("records.db")
        
        # Register cleanup on exit
        atexit.register(self._on_exit)
    
    def __getattr__(self, name: str) -> Union[Collection, Any]:
        """Dynamic collection access and creation."""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # Return a callable that creates records in this collection
        def create_record(**kwargs):
            return Record(name, self, **kwargs)
        
        # Add collection methods to the callable
        create_record.all = lambda: [record.to_dict() for record in self._collections.get(name, [])]
        create_record.get = lambda id: next((record for record in self._collections.get(name, []) if record._id == id), None)
        create_record.delete = lambda id: self._delete_record(name, id)
        create_record.count = lambda: len(self._collections.get(name, []))
        
        return create_record
    
    def __call__(self, collection_name: str, **kwargs) -> Record:
        """Create a new record in the specified collection."""
        return Record(collection_name, self, **kwargs)
    
    def _get_next_id(self, collection_name: str) -> int:
        """Get the next available ID for a collection."""
        if collection_name not in self._next_ids:
            self._next_ids[collection_name] = 0
        current_id = self._next_ids[collection_name]
        self._next_ids[collection_name] += 1
        return current_id
    
    def _add_record(self, collection_name: str, record: Record):
        """Add a record to a collection."""
        if collection_name not in self._collections:
            self._collections[collection_name] = []
        self._collections[collection_name].append(record)
    
    def _delete_record(self, collection_name: str, record_id: int) -> bool:
        """Delete a record by ID from a collection."""
        collection = self._collections.get(collection_name, [])
        for i, record in enumerate(collection):
            if record._id == record_id:
                deleted_record = collection.pop(i)
                self._track_content_change('delete', collection_name, record_id, deleted_record.to_dict())
                return True
        return False
    
    def _get_structure(self, collection_name: str) -> RecordTypeStructure:
        """Get or create the structure for a collection."""
        if collection_name not in self._structures:
            self._structures[collection_name] = RecordTypeStructure(collection_name)
        return self._structures[collection_name]
    
    def _track_content_change(self, action: str, collection_name: str, record_id: int, data: Any):
        """Track content changes."""
        self._content_changes.append({
            'action': action,
            'collection': collection_name,
            'record_id': record_id,
            'data': data
        })
    
    def structure(self) -> Dict[str, Dict[str, str]]:
        """Return the current data structure."""
        result = {}
        for collection_name, structure in self._structures.items():
            result[collection_name] = structure.to_dict()
        return result
    
    def _generate_structure_report(self) -> str:
        """Generate structure change report."""
        all_changes = []
        for structure in self._structures.values():
            all_changes.extend(structure.get_structure_changes())
        
        if not all_changes:
            return "No structure changes."
        
        report = "Structure change report:\n"
        for change in all_changes:
            report += f"+ {change['collection']}.{change['attribute']}: {change['type']}\n"
        return report
    
    def _generate_content_report(self) -> str:
        """Generate content change report showing actual entities created, modified, and deleted."""
        if not self._content_changes:
            return "No content changes."
        
        # Track record states and data
        record_tracking = {}  # (collection, record_id) -> {'state': str, 'data': dict}
        
        for change in self._content_changes:
            key = (change['collection'], change['record_id'])
            
            if change['action'] == 'add':
                record_tracking[key] = {
                    'state': 'created',
                    'data': change['data'],
                    'collection': change['collection']
                }
            elif change['action'] == 'update':
                if key in record_tracking:
                    if record_tracking[key]['state'] == 'created':
                        # Created and modified = still just created
                        continue
                    elif record_tracking[key]['state'] == 'modified':
                        # Already modified, keep as modified
                        continue
                else:
                    # First time seeing this record, must be a modification of existing
                    record_tracking[key] = {
                        'state': 'modified',
                        'data': change['data'],
                        'collection': change['collection']
                    }
            elif change['action'] == 'delete':
                if key in record_tracking and record_tracking[key]['state'] == 'created':
                    # Created then deleted = no net change, remove from tracking
                    del record_tracking[key]
                else:
                    # Was existing (or modified) and deleted
                    record_tracking[key] = {
                        'state': 'deleted',
                        'data': change['data'],
                        'collection': change['collection']
                    }
        
        if not record_tracking:
            return "No net content changes."
        
        # Group by state
        created = [(k, v) for k, v in record_tracking.items() if v['state'] == 'created']
        modified = [(k, v) for k, v in record_tracking.items() if v['state'] == 'modified']
        deleted = [(k, v) for k, v in record_tracking.items() if v['state'] == 'deleted']
        
        report = "Content change report:\n"
        
        # Show created records
        for (collection, record_id), info in created:
            # Show the final state of created records
            current_record = None
            for record in self._collections.get(collection, []):
                if record._id == record_id:
                    current_record = record.to_dict()
                    break
            if current_record:
                report += f"+ {collection}({', '.join(f'{k}={v}' for k, v in current_record.items() if k != 'id')})\n"
        
        # Show modified records
        for (collection, record_id), info in modified:
            current_record = None
            for record in self._collections.get(collection, []):
                if record._id == record_id:
                    current_record = record.to_dict()
                    break
            if current_record:
                report += f"~ {collection}(id={record_id}, {', '.join(f'{k}={v}' for k, v in current_record.items() if k != 'id')})\n"
        
        # Show deleted records
        for (collection, record_id), info in deleted:
            report += f"- {collection}(id={record_id})\n"
        
        return report
    
    def _persist_data(self):
        """Persist data to database."""
        conn = sqlite3.connect(self._db_path)
        try:
            # Create tables for each collection
            for collection_name, records_list in self._collections.items():
                if records_list:
                    # Get all unique columns from all records
                    all_columns = set(['id'])
                    for record in records_list:
                        for attr_name in record.__dict__:
                            if not attr_name.startswith('_'):
                                all_columns.add(attr_name)
                    
                    # Drop and recreate table to handle schema changes
                    conn.execute(f"DROP TABLE IF EXISTS {collection_name}")
                    
                    columns_def = ['id INTEGER PRIMARY KEY']
                    for col in sorted(all_columns):
                        if col != 'id':
                            columns_def.append(f"{col} TEXT")
                    
                    create_table_sql = f"CREATE TABLE {collection_name} ({', '.join(columns_def)})"
                    conn.execute(create_table_sql)
                    
                    # Insert records
                    for record in records_list:
                        record_dict = record.to_dict()
                        # Ensure all columns are present (fill missing with None)
                        full_record = {col: record_dict.get(col) for col in all_columns}
                        
                        placeholders = ', '.join(['?' for _ in full_record])
                        columns_str = ', '.join(full_record.keys())
                        values = list(full_record.values())
                        
                        insert_sql = f"INSERT INTO {collection_name} ({columns_str}) VALUES ({placeholders})"
                        conn.execute(insert_sql, values)
            
            conn.commit()
        finally:
            conn.close()
    
    def _on_exit(self):
        """Called on program exit to persist data and generate reports."""
        self._persist_data()
        
        print(self._generate_structure_report())
        print(self._generate_content_report())
        print("To undo all of the above changes, invoke `records.undo()` once.")
    
    def undo(self):
        """Undo all changes (placeholder for now)."""
        print("Undo functionality not yet implemented.")


# Create the main records instance
records = Records()


# Helper function to create records dynamically
def __getattr__(name: str):
    """Allow module-level access to records collections."""
    if name == 'records':
        return records
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
