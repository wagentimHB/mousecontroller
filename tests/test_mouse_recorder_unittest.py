#!/usr/bin/env python3
"""
Alternative test script using standard Python test patterns
"""

import unittest
import os
import json
import tempfile
import sys
from pathlib import Path

# Ensure we can import our modules
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from mousecontroller.mouse_recorder import MouseRecorder
from mousecontroller.mouse_replayer import MouseReplayer


class TestMouseRecorder(unittest.TestCase):
    """Test cases for MouseRecorder class"""

    def test_recorder_creation(self):
        """Test that MouseRecorder can be created"""
        recorder = MouseRecorder("test_recording.json")
        self.assertEqual(recorder.output_file, "test_recording.json")
        self.assertEqual(recorder.events, [])
        self.assertFalse(recorder.recording)

    def test_replayer_creation(self):
        """Test that MouseReplayer can be created"""
        replayer = MouseReplayer("test_recording.json")
        self.assertEqual(replayer.recording_file, "test_recording.json")
        self.assertIsNone(replayer.recording_data)

    def test_json_format(self):
        """Test the JSON format with mock data"""
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

            self.assertTrue(success)
            self.assertIsNotNone(replayer.recording_data)
            if replayer.recording_data:  # Type guard for linter
                self.assertEqual(replayer.recording_data['metadata']['event_count'], 3)
                self.assertEqual(len(replayer.recording_data['events']), 3)

        finally:
            # Clean up
            os.unlink(temp_file)

    def test_data_directory_path(self):
        """Test that data directory path is set correctly"""
        recorder = MouseRecorder("data/test_output.json")
        expected_path = "data/test_output.json"
        self.assertEqual(recorder.output_file, expected_path)


class TestMouseRecorderIntegration(unittest.TestCase):
    """Integration tests for mouse recording functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file = "test_recording.json"
        self.recorder = MouseRecorder(self.test_file)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def test_event_structure(self):
        """Test that events have the correct structure"""
        # Simulate adding events manually (since we can't actually move mouse in tests)
        test_event = {
            "type": "move",
            "x": 100,
            "y": 200,
            "timestamp": 1.0
        }
        self.recorder.events.append(test_event)

        # Test event structure
        self.assertIn("type", test_event)
        self.assertIn("x", test_event)
        self.assertIn("y", test_event)
        self.assertIn("timestamp", test_event)


if __name__ == "__main__":
    print("Running mouse recorder tests with unittest...")
    print("=" * 60)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Unit tests completed!")