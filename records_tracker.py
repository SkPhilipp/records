"""
RecordsTracker - Handles content change tracking and reporting for Records.
"""

from typing import Any, Dict, List, Tuple


class RecordsTracker:
    """Tracks and reports content changes for Records collections."""
    
    def __init__(self):
        self._content_changes: List[Dict[str, Any]] = []
    
    def track_change(self, action: str, collection_name: str, record_id: int, data: Any) -> None:
        """Track a content change."""
        self._content_changes.append({
            'action': action,
            'collection': collection_name,
            'record_id': record_id,
            'data': data
        })
    
    def clear_changes(self) -> None:
        """Clear all tracked changes."""
        self._content_changes.clear()
    
    def get_changes(self) -> List[Dict[str, Any]]:
        """Get all tracked changes."""
        return self._content_changes.copy()
    
    def generate_report(self, collections: Dict[str, List['Record']]) -> str:
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
            for record in collections.get(collection, []):
                if record._id == record_id:
                    current_record = record.to_dict()
                    break
            if current_record:
                report += f"+ {collection}({', '.join(f'{k}={v}' for k, v in current_record.items() if k != 'id')})\n"
        
        # Show modified records
        for (collection, record_id), info in modified:
            current_record = None
            for record in collections.get(collection, []):
                if record._id == record_id:
                    current_record = record.to_dict()
                    break
            if current_record:
                report += f"~ {collection}(id={record_id}, {', '.join(f'{k}={v}' for k, v in current_record.items() if k != 'id')})\n"
        
        # Show deleted records
        for (collection, record_id), info in deleted:
            report += f"- {collection}(id={record_id})\n"
        
        return report
