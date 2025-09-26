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
        self.replay_times = 1  # Default replay count
        self.replay_hours = 0  # Default replay hours (0 = disabled)
        self.replay_latency = 2.0  # Default latency between replays in seconds
        
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
            
    def set_replay_times(self, times):
        """Set the number of times to replay the recording
        
        Args:
            times (int): Number of times to replay (must be positive)
        
        Returns:
            bool: True if successful, False if invalid input
        """
        if not isinstance(times, int) or times < 1:
            print("Replay times must be a positive integer")
            return False
        
        self.replay_times = times
        print(f"Replay times set to: {times}")
        return True
    
    def set_replay_hours(self, hours):
        """Set the number of hours to continuously replay the recording
        
        Args:
            hours (float): Number of hours to replay (must be positive)
        
        Returns:
            bool: True if successful, False if invalid input
        """
        if not isinstance(hours, (int, float)) or hours < 0:
            print("Replay hours must be a positive number")
            return False
        
        self.replay_hours = hours
        if hours > 0:
            print(f"Replay hours set to: {hours:.2f} hours")
        else:
            print("Replay hours disabled (set to 0)")
        return True
    
    def set_replay_latency(self, latency):
        """Set the latency (pause) between replays in seconds
        
        Args:
            latency (float): Latency in seconds between replays (must be >= 0)
        
        Returns:
            bool: True if successful, False if invalid input
        """
        if not isinstance(latency, (int, float)) or latency < 0:
            print("Replay latency must be a non-negative number")
            return False
        
        self.replay_latency = float(latency)
        if latency > 0:
            print(f"Replay latency set to: {latency:.2f} seconds")
        else:
            print("Replay latency set to 0 (no pause between replays)")
        return True
    
    def replay_multiple(self, speed=1.0, delay_start=3, times=None):
        """Replay the recorded mouse events multiple times
        
        Args:
            speed (float): Replay speed multiplier (1.0 = normal speed)
            delay_start (int): Delay in seconds before starting
            times (int): Number of times to replay (uses self.replay_times if None)
        
        Returns:
            bool: True if successful, False if error occurred
        """
        if not self.recording_data:
            print("No recording data loaded")
            return False
            
        replay_count = times if times is not None else self.replay_times
        
        if replay_count < 1:
            print("Replay times must be at least 1")
            return False
            
        events = self.recording_data['events']
        
        if not events:
            print("No events to replay")
            return False
            
        print(f"Starting replay {replay_count} time(s) in {delay_start} seconds...")
        print(f"Speed: {speed}x")
        print("Press Ctrl+C to stop replay")
        
        # Initial countdown
        for i in range(delay_start, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        try:
            for replay_num in range(replay_count):
                print(f"\nReplay {replay_num + 1}/{replay_count}...")
                
                # Execute the replay
                if not self._execute_replay_sequence(events, speed):
                    return False
                
                # Add configurable pause between replays (except for last one)
                if replay_num < replay_count - 1:
                    if self.replay_latency > 0:
                        print(f"Waiting {self.replay_latency:.2f} seconds "
                              f"before next replay...")
                        time.sleep(self.replay_latency)
                    else:
                        print("No pause between replays (latency = 0)")
                    
            print(f"\nAll replays completed! Executed {replay_count} "
                  f"replay(s)")
            return True
            
        except KeyboardInterrupt:
            print(f"\nReplay interrupted by user after {replay_num + 1} "
                  f"replay(s)")
            return False
        except Exception as e:
            print(f"\nError during replay: {e}")
            return False
    
    def _execute_replay_sequence(self, events, speed):
        """Execute a single replay sequence
        
        Args:
            events (list): List of events to replay
            speed (float): Replay speed multiplier
            
        Returns:
            bool: True if successful, False if interrupted
        """
        try:
            start_time = time.time()
            
            for i, event in enumerate(events):
                # Calculate delay based on timestamp and replay speed
                target_time = event['timestamp'] / speed
                current_elapsed = time.time() - start_time
                delay = target_time - current_elapsed
                
                if delay > 0:
                    time.sleep(delay)
                    
                self._execute_event(event)
                
                # Progress indicator
                if i % 100 == 0:
                    progress = (i / len(events)) * 100
                    print(f"Progress: {progress:.1f}% ({i}/{len(events)})", 
                          end='\r')
                    
            return True
            
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by caller
        except Exception as e:
            print(f"Error in replay sequence: {e}")
            return False
    
    def replay_for_hours(self, speed=1.0, delay_start=3, hours=None):
        """Replay the recorded mouse events continuously for specified hours
        
        Args:
            speed (float): Replay speed multiplier (1.0 = normal speed)
            delay_start (int): Delay in seconds before starting
            hours (float): Number of hours to replay (uses 
                self.replay_hours if None)
        
        Returns:
            bool: True if completed successfully, False if error occurred
        """
        if not self.recording_data:
            print("No recording data loaded")
            return False
            
        replay_hours = hours if hours is not None else self.replay_hours
        
        if replay_hours <= 0:
            print("Replay hours must be greater than 0")
            return False
            
        events = self.recording_data['events']
        
        if not events:
            print("No events to replay")
            return False
            
        # Calculate end time
        end_time = time.time() + (replay_hours * 3600)  # Hours to seconds
        
        print(f"Starting continuous replay for {replay_hours:.2f} hour(s)...")
        print(f"Speed: {speed}x")
        end_time_str = time.strftime('%H:%M:%S', time.localtime(end_time))
        print(f"Will stop at: {end_time_str}")
        print("Press Ctrl+C to stop replay early")
        
        # Initial countdown
        for i in range(delay_start, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        try:
            replay_count = 0
            
            while time.time() < end_time:
                replay_count += 1
                remaining_time = end_time - time.time()
                
                hours_remaining = remaining_time / 3600
                print(f"\nReplay #{replay_count} (Time remaining: "
                      f"{hours_remaining:.2f} hours)")
                
                # Check if we have enough time for at least one more replay
                recording_duration = self.recording_data['metadata'][
                    'duration'] / speed
                if remaining_time < recording_duration:
                    print("Not enough time remaining for a complete replay. "
                          "Stopping.")
                    break
                
                # Execute the replay
                if not self._execute_replay_sequence(events, speed):
                    return False
                
                # Configurable pause between replays
                if time.time() < end_time:
                    if self.replay_latency > 0:
                        print(f"Waiting {self.replay_latency:.2f} seconds "
                              f"before next replay...")
                        time.sleep(self.replay_latency)
                    else:
                        print("No pause between replays (latency = 0)")
                    
            print(f"\nTime-based replay completed! Executed {replay_count} "
                  f"replays in {replay_hours:.2f} hours")
            return True
            
        except KeyboardInterrupt:
            start_time = end_time - replay_hours * 3600
            elapsed_hours = (time.time() - start_time) / 3600
            print(f"\nReplay interrupted by user after {replay_count} "
                  f"replays ({elapsed_hours:.2f} hours)")
            return False
        except Exception as e:
            print(f"\nError during time-based replay: {e}")
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
                duration = self.recording_data['metadata']['duration']
                print(f"Duration: {duration:.2f} seconds")
            
            print(f"Current replay times: {self.replay_times}")
            print(f"Current replay speed: {self.replay_speed}x")
            print(f"Current replay hours: {self.replay_hours:.2f} hours")
            
            print("\nOptions:")
            print("1. Replay at normal speed (1x)")
            print("2. Replay at half speed (0.5x)")
            print("3. Replay at double speed (2x)")
            print("4. Custom replay speed")
            print("5. Set replay times (how many times to repeat)")
            print("6. Set replay hours (continuous replay for X hours)")
            print("7. Set replay latency (pause between replays)")
            print("8. Replay multiple times with current settings")
            print("9. Replay for hours with current settings")
            print("10. Load different recording file")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-10): ").strip()
            
            if choice == '1':
                self.replay(speed=1.0)
            elif choice == '2':
                self.replay(speed=0.5)
            elif choice == '3':
                self.replay(speed=2.0)
            elif choice == '4':
                try:
                    speed_input = input("Enter replay speed (e.g., 1.0 for normal, 0.5 for half): ")
                    speed = float(speed_input)
                    if speed <= 0:
                        print("Speed must be positive")
                        continue
                    self.replay_speed = speed
                    self.replay(speed=speed)
                except ValueError:
                    print("Invalid speed value")
            elif choice == '5':
                try:
                    times_input = input("Enter number of replay times (e.g., 3): ")
                    times = int(times_input)
                    if self.set_replay_times(times):
                        print(f"Replay times updated to: {times}")
                except ValueError:
                    print("Invalid number. Please enter a positive integer.")
            elif choice == '6':
                try:
                    hours_input = input("Enter replay hours (e.g., 0.5 for 30 minutes): ")
                    hours = float(hours_input)
                    if self.set_replay_hours(hours):
                        print(f"Replay hours updated to: {hours:.2f}")
                except ValueError:
                    print("Invalid number. Please enter a positive number.")
            elif choice == '7':
                try:
                    latency_input = input("Enter pause between replays in "
                                          "seconds (e.g., 2.0): ")
                    latency = float(latency_input)
                    if self.set_replay_latency(latency):
                        print(f"Replay latency updated to: {latency:.1f} "
                              f"seconds")
                except ValueError:
                    print("Invalid number. Please enter a non-negative "
                          "number.")
            elif choice == '8':
                delay_input = input("Enter start delay in seconds (default: 3): ").strip()
                try:
                    delay = int(delay_input) if delay_input else 3
                except ValueError:
                    delay = 3
                self.replay_multiple(speed=self.replay_speed, delay_start=delay)
            elif choice == '9':
                if self.replay_hours <= 0:
                    print("Please set replay hours first (option 6)")
                    continue
                delay_input = input("Enter start delay in seconds (default: 3): ").strip()
                try:
                    delay = int(delay_input) if delay_input else 3
                except ValueError:
                    delay = 3
                self.replay_for_hours(speed=self.replay_speed, delay_start=delay)
            elif choice == '10':
                filename = input("Enter recording file path: ").strip()
                if filename:
                    self.recording_file = filename
                    if not self.load_recording():
                        # Reset to default
                        self.recording_file = "data/mouse_recording.json"
            elif choice == '0':
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
