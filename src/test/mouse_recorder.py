#!/usr/bin/env python3
"""
Mouse Recorder - Records mouse movements, clicks, and scroll actions
Press ESC to stop recording
"""

import json
import time
from datetime import datetime
from pynput import mouse
from pynput.mouse import Button
import threading
import os


class MouseRecorder:
    def __init__(self, output_file="mouse_recording.json"):
        self.output_file = output_file
        self.events = []
        self.start_time = None
        self.recording = False
        self.listener = None
        
    def start_recording(self):
        """Start recording mouse events"""
        print(f"Starting mouse recording... Press ESC to stop")
        print(f"Recording will be saved to: {self.output_file}")
        
        self.recording = True
        self.start_time = time.time()
        self.events = []
        
        # Start mouse listener
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
        self.listener.start()
        
        # Monitor for ESC key to stop recording
        self._monitor_stop_key()
        
    def stop_recording(self):
        """Stop recording and save to file"""
        if not self.recording:
            return
            
        self.recording = False
        if self.listener:
            self.listener.stop()
        
        self.save_recording()
        print(f"\nRecording stopped. {len(self.events)} events recorded.")
        print(f"Recording saved to: {self.output_file}")
        
    def on_move(self, x, y):
        """Handle mouse move events"""
        if not self.recording:
            return
            
        event = {
            "type": "move",
            "x": x,
            "y": y,
            "timestamp": time.time() - self.start_time
        }
        self.events.append(event)
        
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.recording:
            return
            
        event = {
            "type": "click",
            "x": x,
            "y": y,
            "button": button.name,
            "pressed": pressed,
            "timestamp": time.time() - self.start_time
        }
        self.events.append(event)
        print(f"{'Press' if pressed else 'Release'} {button.name} at ({x}, {y})")
        
    def on_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        if not self.recording:
            return
            
        event = {
            "type": "scroll",
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
            "timestamp": time.time() - self.start_time
        }
        self.events.append(event)
        print(f"Scroll at ({x}, {y}) - dx: {dx}, dy: {dy}")
        
    def _monitor_stop_key(self):
        """Monitor for ESC key press to stop recording"""
        from pynput import keyboard
        
        def on_key_press(key):
            try:
                if key == keyboard.Key.esc:
                    print("\nESC pressed - stopping recording...")
                    self.stop_recording()
                    return False  # Stop listener
            except AttributeError:
                pass
                
        # Start keyboard listener in a separate thread
        keyboard_listener = keyboard.Listener(on_press=on_key_press)
        keyboard_listener.start()
        keyboard_listener.join()
        
    def save_recording(self):
        """Save recorded events to JSON file"""
        recording_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "duration": time.time() - self.start_time if self.start_time else 0,
                "event_count": len(self.events)
            },
            "events": self.events
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        
        try:
            with open(self.output_file, 'w') as f:
                json.dump(recording_data, f, indent=2)
        except Exception as e:
            print(f"Error saving recording: {e}")
            
    def load_recording(self, filename=None):
        """Load recording from JSON file"""
        file_to_load = filename or self.output_file
        
        try:
            with open(file_to_load, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print(f"Recording file not found: {file_to_load}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {file_to_load}")
            return None
        except Exception as e:
            print(f"Error loading recording: {e}")
            return None


def main():
    """Main function to run the mouse recorder"""
    import sys
    
    output_file = "data/mouse_recording.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    recorder = MouseRecorder(output_file)
    
    try:
        recorder.start_recording()
    except KeyboardInterrupt:
        print("\nRecording interrupted by user")
        recorder.stop_recording()
    except Exception as e:
        print(f"Error during recording: {e}")
        recorder.stop_recording()


if __name__ == "__main__":
    main()