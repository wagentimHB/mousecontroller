#!/usr/bin/env python3
"""
Mouse Recorder/Replayer Demo
Demonstrates how to use the mouse recording and replay functionality
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "test"
sys.path.insert(0, str(src_path))

from mouse_recorder import MouseRecorder
from mouse_replayer import MouseReplayer


def demo_recording():
    """Demonstrate mouse recording"""
    print("="*60)
    print("MOUSE RECORDING DEMO")
    print("="*60)
    print("This will start recording your mouse movements and clicks.")
    print("Move your mouse around and click a few times.")
    print("Press ESC when you're done recording.")
    print("="*60)
    
    input("Press Enter to start recording...")
    
    # Create recorder instance
    recorder = MouseRecorder("data/demo_recording.json")
    
    try:
        recorder.start_recording()
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
        recorder.stop_recording()
    except Exception as e:
        print(f"Error during recording: {e}")


def demo_replay():
    """Demonstrate mouse replay"""
    print("="*60)
    print("MOUSE REPLAY DEMO")
    print("="*60)
    
    # Check if recording exists
    recording_file = "data/demo_recording.json"
    if not os.path.exists(recording_file):
        print(f"No recording found at {recording_file}")
        print("Please run the recording demo first.")
        return
        
    print("This will replay your recorded mouse movements.")
    print("Make sure to position your mouse cursor appropriately.")
    print("The replay will start in a few seconds.")
    print("="*60)
    
    input("Press Enter to start replay...")
    
    # Create replayer instance
    replayer = MouseReplayer(recording_file)
    
    if replayer.load_recording():
        replayer.replay(speed=1.0, delay_start=3)


def main():
    """Main demo function"""
    print("MOUSE RECORDER/REPLAYER DEMO")
    print("="*40)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Record mouse movements and clicks")
        print("2. Replay recorded movements")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            demo_recording()
        elif choice == '2':
            demo_replay()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()