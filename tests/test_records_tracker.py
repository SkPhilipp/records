"""
Test RecordsTracker functionality.
"""

from src.records_tracker import RecordsTracker


class MockRecord:
    """Mock Record class for testing."""
    def __init__(self, record_id: int, **kwargs):
        self._id = record_id
        self.__dict__.update(kwargs)
    
    def to_dict(self):
        result = {'id': self._id}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result


def test_basic_tracking():
    """Test basic change tracking functionality."""
    print("Testing basic tracking...")
    
    tracker = RecordsTracker()
    
    # Test initial state
    assert len(tracker.get_changes()) == 0
    assert tracker.generate_report({}) == "No content changes."
    
    # Track some changes
    tracker.track_change('add', 'users', 1, {'name': 'Alice', 'age': 30})
    tracker.track_change('add', 'users', 2, {'name': 'Bob', 'age': 25})
    
    changes = tracker.get_changes()
    assert len(changes) == 2
    assert changes[0]['action'] == 'add'
    assert changes[0]['collection'] == 'users'
    assert changes[0]['record_id'] == 1
    
    print("✓ Basic tracking works")


def test_clear_changes():
    """Test clearing changes."""
    print("Testing clear changes...")
    
    tracker = RecordsTracker()
    tracker.track_change('add', 'users', 1, {'name': 'Alice'})
    
    assert len(tracker.get_changes()) == 1
    
    tracker.clear_changes()
    assert len(tracker.get_changes()) == 0
    assert tracker.generate_report({}) == "No content changes."
    
    print("✓ Clear changes works")


def test_report_generation():
    """Test report generation with mock collections."""
    print("Testing report generation...")
    
    tracker = RecordsTracker()
    
    # Create mock collections
    collections = {
        'users': [
            MockRecord(1, name='Alice', age=30),
            MockRecord(2, name='Bob', age=25)
        ]
    }
    
    # Track creation
    tracker.track_change('add', 'users', 1, {'name': 'Alice', 'age': 30})
    tracker.track_change('add', 'users', 2, {'name': 'Bob', 'age': 25})
    
    report = tracker.generate_report(collections)
    assert "+ users(name=Alice, age=30)" in report
    assert "+ users(name=Bob, age=25)" in report
    
    print("✓ Report generation works")


def test_create_then_delete():
    """Test that create+delete results in no net change."""
    print("Testing create then delete...")
    
    tracker = RecordsTracker()
    collections = {}
    
    # Create then delete
    tracker.track_change('add', 'users', 1, {'name': 'Alice'})
    tracker.track_change('delete', 'users', 1, {'id': 1, 'name': 'Alice'})
    
    report = tracker.generate_report(collections)
    assert report == "No net content changes."
    
    print("✓ Create then delete cancels out")


def test_create_then_modify():
    """Test that create+modify only shows as create."""
    print("Testing create then modify...")
    
    tracker = RecordsTracker()
    collections = {
        'users': [MockRecord(1, name='Alice Updated', age=31)]
    }
    
    # Create then modify
    tracker.track_change('add', 'users', 1, {'name': 'Alice', 'age': 30})
    tracker.track_change('update', 'users', 1, {'name': {'old': 'Alice', 'new': 'Alice Updated'}})
    tracker.track_change('update', 'users', 1, {'age': {'old': 30, 'new': 31}})
    
    report = tracker.generate_report(collections)
    assert "+ users(name=Alice Updated, age=31)" in report
    assert "~" not in report  # No modify symbol should appear
    
    print("✓ Create then modify shows only as create")


def test_modify_existing():
    """Test modifying existing records."""
    print("Testing modify existing...")
    
    tracker = RecordsTracker()
    collections = {
        'users': [MockRecord(1, name='Alice Updated', age=31)]
    }
    
    # Only modification (no prior add in this session)
    tracker.track_change('update', 'users', 1, {'name': {'old': 'Alice', 'new': 'Alice Updated'}})
    
    report = tracker.generate_report(collections)
    assert "~ users(id=1, name=Alice Updated, age=31)" in report
    
    print("✓ Modify existing works")


def test_delete_existing():
    """Test deleting existing records."""
    print("Testing delete existing...")
    
    tracker = RecordsTracker()
    collections = {}
    
    # Only deletion (no prior add in this session)
    tracker.track_change('delete', 'users', 1, {'id': 1, 'name': 'Alice'})
    
    report = tracker.generate_report(collections)
    assert "- users(id=1)" in report
    
    print("✓ Delete existing works")


if __name__ == "__main__":
    test_basic_tracking()
    test_clear_changes()
    test_report_generation()
    test_create_then_delete()
    test_create_then_modify()
    test_modify_existing()
    test_delete_existing()
    print("\nAll RecordsTracker tests passed! ✅")
