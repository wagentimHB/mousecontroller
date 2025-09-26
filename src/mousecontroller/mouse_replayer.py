#!/usr/bin/env python3
"""
Mouse Replayer - Replays recorded mouse movements, clicks, and scroll actions
"""

import json
import time
import sys
import os
from pynput.mouse import Button, Listener
from pynput import mouse


class MouseReplayer:
    def __init__(self, recording_file="data/mouse_recording.json"):
        self.recording_file = recording_file
        self.controller = mouse.Controller()
        self.recording_data = None
        self.replay_speed = 1.0  # Normal speed
        
    def load_recording(self, filename=None):
        """Load recording from JSON file"""
        file_to_load = filename or self.recording_file
        
        try:
            with open(file_to_load, 'r') as f:
                self.recording_data = json.load(f)
                print(f"Loaded recording: {file_to_load}")
                print(f"Duration: {self.recording_data['metadata']['duration']:.2f} seconds")
                print(f"Events: {self.recording_data['metadata']['event_count']}")
                return True
        except FileNotFoundError:
            print(f"Recording file not found: {file_to_load}")
            return False
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {file_to_load}")
            return False
        except Exception as e:
            print(f"Error loading recording: {e}")
            return False
            
    def replay(self, speed=1.0, delay_start=3):
        """Replay the recorded mouse events"""
        if not self.recording_data:
            print("No recording data loaded")
            return False
            
        self.replay_speed = speed
        events = self.recording_data['events']
        
        if not events:
            print("No events to replay")
            return False
            
        print(f"Starting replay in {delay_start} seconds...")
        print("Press Ctrl+C to stop replay")
        
        # Countdown
        for i in range(delay_start, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        print("Replaying...")
        
        try:
            start_time = time.time()
            last_timestamp = 0
            
            for i, event in enumerate(events):
                # Calculate delay based on timestamp and replay speed
                target_time = event['timestamp'] / self.replay_speed
                current_elapsed = time.time() - start_time
                delay = target_time - current_elapsed
                
                if delay > 0:
                    time.sleep(delay)
                    
                self._execute_event(event)
                
                # Progress indicator
                if i % 100 == 0:
                    progress = (i / len(events)) * 100
                    print(f"Progress: {progress:.1f}% ({i}/{len(events)})", end='\r')
                    
            print(f"\nReplay completed! Executed {len(events)} events")
            return True
            
        except KeyboardInterrupt:
            print("\nReplay interrupted by user")
            return False
        except Exception as e:
            print(f"\nError during replay: {e}")
            return False
            
    def _execute_event(self, event):
        """Execute a single mouse event"""
        event_type = event['type']
        
        try:
            if event_type == 'move':
                self.controller.position = (event['x'], event['y'])
                
            elif event_type == 'click':
                self.controller.position = (event['x'], event['y'])
                button = Button.left if event['button'] == 'left' else Button.right
                if event['button'] == 'middle':
                    button = Button.middle
                    
                if event['pressed']:
                    self.controller.press(button)
                else:
                    self.controller.release(button)
                    
            elif event_type == 'scroll':
                self.controller.position = (event['x'], event['y'])
                self.controller.scroll(event['dx'], event['dy'])
                
        except Exception as e:
            print(f"Error executing event {event_type}: {e}")
            
    def replay_with_options(self):
        """Interactive replay with user options"""
        if not self.load_recording():
            return
            
        print("\n" + "="*50)
        print("MOUSE REPLAY OPTIONS")
        print("="*50)
        
        while True:
            print(f"\nCurrent recording: {self.recording_file}")
            if self.recording_data:
                print(f"Events: {self.recording_data['metadata']['event_count']}")
                print(f"Duration: {self.recording_data['metadata']['duration']:.2f} seconds")
            
            print("\nOptions:")
            print("1. Replay at normal speed (1x)")
            print("2. Replay at half speed (0.5x)")
            print("3. Replay at double speed (2x)")
            print("4. Custom replay speed")
            print("5. Load different recording file")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.replay(speed=1.0)
            elif choice == '2':
                self.replay(speed=0.5)
            elif choice == '3':
                self.replay(speed=2.0)
            elif choice == '4':
                try:
                    speed = float(input("Enter replay speed (e.g., 1.0 for normal, 0.5 for half): "))
                    if speed <= 0:
                        print("Speed must be positive")
                        continue
                    self.replay(speed=speed)
                except ValueError:
                    print("Invalid speed value")
            elif choice == '5':
                filename = input("Enter recording file path: ").strip()
                if filename:
                    self.recording_file = filename
                    if not self.load_recording():
                        self.recording_file = "data/mouse_recording.json"  # Reset to default
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


def main():
    """Main function to run the mouse replayer"""
    recording_file = "data/mouse_recording.json"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        recording_file = sys.argv[1]
        
    replayer = MouseReplayer(recording_file)
    
    # Check if file exists
    if not os.path.exists(recording_file):
        print(f"Recording file not found: {recording_file}")
        print("Please run mouse_recorder.py first to create a recording.")
        return
        
    if len(sys.argv) > 2:
        # Command line mode with speed parameter
        try:
            speed = float(sys.argv[2])
            if replayer.load_recording():
                replayer.replay(speed=speed)
        except ValueError:
            print("Invalid speed parameter. Using interactive mode.")
            replayer.replay_with_options()
    else:
        # Interactive mode
        replayer.replay_with_options()


if __name__ == "__main__":
    main()