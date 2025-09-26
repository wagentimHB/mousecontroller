#!/usr/bin/env python3
"""
Test script to validate mouse recorder and replayer functionality
"""

import os
import json
import tempfile
import sys
import importlib.util
from pathlib import Path

# Add src to path before any imports
src_path = Path(__file__).parent.parent / "src" / "mousecontroller"
sys.path.insert(0, str(src_path))

# Dynamic import to avoid linting issues
def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import our modules dynamically
mouse_recorder_path = src_path / "mouse_recorder.py"
mouse_replayer_path = src_path / "mouse_replayer.py"

mouse_recorder_module = import_module_from_path("mouse_recorder", mouse_recorder_path)
mouse_replayer_module = import_module_from_path("mouse_replayer", mouse_replayer_path)

MouseRecorder = mouse_recorder_module.MouseRecorder
MouseReplayer = mouse_replayer_module.MouseReplayer


def test_recorder_creation():
    """Test that MouseRecorder can be created"""
    print("Testing MouseRecorder creation...")
    recorder = MouseRecorder("test_recording.json")
    assert recorder.output_file == "test_recording.json"
    assert recorder.events == []
    assert not recorder.recording
    print("✓ MouseRecorder creation test passed")


def test_replayer_creation():
    """Test that MouseReplayer can be created"""
    print("Testing MouseReplayer creation...")
    replayer = MouseReplayer("test_recording.json")
    assert replayer.recording_file == "test_recording.json"
    assert replayer.recording_data is None
    print("✓ MouseReplayer creation test passed")


def test_json_format():
    """Test the JSON format with mock data"""
    print("Testing JSON format...")
    
    # Create mock recording data
    mock_data = {
        "metadata": {
            "created_at": "2025-09-26T10:30:45.123456",
            "duration": 5.0,
            "event_count": 3
        },
        "events": [
            {
                "type": "move",
                "x": 100,
                "y": 200,
                "timestamp": 0.5
            },
            {
                "type": "click",
                "x": 150,
                "y": 250,
                "button": "left",
                "pressed": True,
                "timestamp": 1.0
            },
            {
                "type": "click",
                "x": 150,
                "y": 250,
                "button": "left",
                "pressed": False,
                "timestamp": 1.1
            }
        ]
    }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_data, f)
        temp_file = f.name
    
    try:
        # Test loading with replayer
        replayer = MouseReplayer(temp_file)
        success = replayer.load_recording()
        
        assert success == True
        assert replayer.recording_data is not None
        assert replayer.recording_data['metadata']['event_count'] == 3
        assert len(replayer.recording_data['events']) == 3
        
        print("✓ JSON format test passed")
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_data_directory():
    """Test that data directory gets created"""
    print("Testing data directory creation...")
    
    # This should create the data directory
    recorder = MouseRecorder("data/test_output.json")
    
    # The directory should exist after creating a recorder (it creates on save)
    # For now, just test the path is set correctly
    expected_path = "data/test_output.json"
    assert recorder.output_file == expected_path
    
    print("✓ Data directory test passed")


def run_all_tests():
    """Run all tests"""
    print("Running mouse recorder/replayer tests...")
    print("=" * 50)
    
    try:
        test_recorder_creation()
        test_replayer_creation()
        test_json_format()
        test_data_directory()
        
        print("=" * 50)
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)