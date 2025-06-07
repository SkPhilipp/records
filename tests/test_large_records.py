"""
Test that large records are properly truncated in change reports.
"""

import tempfile
import shutil
from pathlib import Path
from src.records import Records


def test_large_record_truncation():
    """Test that large records are truncated in change reports."""
    print("Testing large record truncation...")
    
    # Create a temporary directory for this test
    temp_dir = Path(tempfile.mkdtemp())
    json_path = temp_dir / "test_large_records.json"
    
    try:
        records = Records(json_path)
        
        # Create a record with a very long string to make it exceed the limit
        long_text = "A" * 200  # 200 characters
        records.test_record(
            short_field="normal",
            very_long_field=long_text,
            another_field="also normal"
        )
        
        # Get the change report
        report = records._tracker.generate_report(records._collections)
        
        # Verify that the report contains the truncation warning
        assert "[truncated" in report, f"Expected '[truncated' in report but got: {report}"
        
        # Verify that the report is not excessively long
        lines = report.split('\n')
        content_line = None
        for line in lines:
            if line.startswith('+ test_record('):
                content_line = line
                break
        
        assert content_line is not None, "Could not find the content line in report"
        assert len(content_line) < 150, f"Content line too long: {len(content_line)} chars"
        
        print("✓ Large record truncation works correctly")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_normal_record_not_truncated():
    """Test that normal-sized records are not truncated."""
    print("Testing normal record not truncated...")
    
    # Create a temporary directory for this test
    temp_dir = Path(tempfile.mkdtemp())
    json_path = temp_dir / "test_normal_records.json"
    
    try:
        records = Records(json_path)
        
        # Create a record with normal-sized data
        records.test_record(
            name="John Doe",
            age=30,
            city="Amsterdam"
        )
        
        # Get the change report
        report = records._tracker.generate_report(records._collections)
        
        # Verify that the report does NOT contain the truncation warning
        assert "[truncated" not in report, f"Unexpected '[truncated' in report: {report}"
        
        # Verify that all fields are present
        assert "name=John Doe" in report
        assert "age=30" in report
        assert "city=Amsterdam" in report
        
        print("✓ Normal record not truncated")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_large_record_truncation()
    test_normal_record_not_truncated()
    print("\nAll large record tests passed! ✅")
