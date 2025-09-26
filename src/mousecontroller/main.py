#!/usr/bin/env python3
"""
Mouse Recorder & Replayer - Main Entry Point
Command-line interface for mouse recording and replay functionality
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import utilities
from utils import get_mousecontroller_modules, import_gui_module


# Import our modules
try:
    MouseRecorder, MouseReplayer = get_mousecontroller_modules(current_dir)
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure mouse_recorder.py and mouse_replayer.py are in the "
          "same directory.")
    sys.exit(1)


def show_banner():
    """Display application banner"""
    print("=" * 80)
    print("🐭 MOUSE RECORDER & REPLAYER")
    print("=" * 80)
    print("A comprehensive tool for recording and replaying mouse actions")
    print("Version: 1.0.0")
    print("=" * 80)


def cmd_record(args):
    """Handle record command"""
    print("Starting mouse recording...")
    print(f"Output file: {args.output}")
    print("Move your mouse and click as needed. Press ESC to stop recording.")
    print("-" * 40)
    
    recorder = MouseRecorder(args.output)
    try:
        recorder.start_recording()
        print("\n✅ Recording completed successfully!")
        print(f"📁 File saved: {args.output}")
        if recorder.events:
            print(f"📊 Events recorded: {len(recorder.events)}")
    except KeyboardInterrupt:
        print("\n⚠️ Recording interrupted by user")
        recorder.stop_recording()
    except Exception as e:
        print(f"\n❌ Recording failed: {e}")
        return 1
    
    return 0


def cmd_replay(args):
    """Handle replay command"""
    if not os.path.exists(args.file):
        print(f"❌ Recording file not found: {args.file}")
        return 1
        
    print(f"Loading recording: {args.file}")
    print(f"Replay speed: {args.speed}x")
    print(f"Start delay: {args.delay} seconds")
    print("-" * 40)
    
    replayer = MouseReplayer(args.file)
    
    if not replayer.load_recording():
        print("❌ Failed to load recording file")
        return 1
        
    # Show recording info
    metadata = replayer.recording_data.get('metadata', {})
    print("📄 Recording info:")
    print(f"   Duration: {metadata.get('duration', 0):.2f} seconds")
    print(f"   Events: {metadata.get('event_count', 0)}")
    print(f"   Created: {metadata.get('created_at', 'Unknown')}")
    print()
    
    try:
        replayer.replay(speed=args.speed, delay_start=args.delay)
        print("✅ Replay completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️ Replay interrupted by user")
    except Exception as e:
        print(f"❌ Replay failed: {e}")
        return 1
    
    return 0


def cmd_gui(args):
    """Handle GUI command"""
    try:
        # Import GUI module dynamically
        gui_module = import_gui_module(current_dir)
        print("🚀 Starting GUI application...")
        gui_module.main()
    except ImportError:
        print("❌ GUI dependencies not available.")
        print("Please install PyQt6: pip install PyQt6")
        return 1
    except Exception as e:
        print(f"❌ Failed to start GUI: {e}")
        return 1
    
    return 0


def cmd_info(args):
    """Handle info command"""
    if not os.path.exists(args.file):
        print(f"❌ Recording file not found: {args.file}")
        return 1
        
    print(f"📄 Recording Information: {args.file}")
    print("-" * 40)
    
    replayer = MouseReplayer(args.file)
    if not replayer.load_recording():
        print("❌ Failed to load recording file")
        return 1
        
    data = replayer.recording_data
    metadata = data.get('metadata', {})
    events = data.get('events', [])
    
    # Basic info
    print(f"Created: {metadata.get('created_at', 'Unknown')}")
    print(f"Duration: {metadata.get('duration', 0):.2f} seconds")
    print(f"Total Events: {metadata.get('event_count', 0)}")
    print(f"File Size: {os.path.getsize(args.file)} bytes")
    
    # Event breakdown
    if events:
        event_types = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
        print("\n📊 Event Breakdown:")
        for event_type, count in event_types.items():
            print(f"   {event_type.capitalize()}: {count}")
    
    return 0


def cmd_list_recordings(args):
    """Handle list command"""
    data_dir = Path(args.directory)
    if not data_dir.exists():
        print(f"📁 Directory not found: {args.directory}")
        return 1
        
    print(f"📁 Recordings in: {args.directory}")
    print("-" * 60)
    
    json_files = list(data_dir.glob("*.json"))
    
    if not json_files:
        print("No recording files found.")
        return 0
        
    for file_path in sorted(json_files):
        try:
            replayer = MouseReplayer(str(file_path))
            if replayer.load_recording():
                metadata = replayer.recording_data.get('metadata', {})
                duration = metadata.get('duration', 0)
                event_count = metadata.get('event_count', 0)
                created_raw = metadata.get('created_at', 'Unknown')
                created = created_raw[:19].replace('T', ' ')
                
                print(f"📄 {file_path.name}")
                print(f"   Created: {created}")
                print(f"   Duration: {duration:.2f}s | Events: {event_count}")
                print()
        except Exception:
            print(f"❌ {file_path.name} (corrupted or invalid)")
            print()
    
    return 0


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Mouse Recorder & Replayer - Record and replay mouse "
                    "actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s record -o my_recording.json          # Record mouse actions
  %(prog)s replay my_recording.json             # Replay at normal speed
  %(prog)s replay my_recording.json -s 0.5      # Replay at half speed
  %(prog)s replay my_recording.json -s 2 -d 5   # Double speed with 5s delay
  %(prog)s gui                                   # Launch GUI interface
  %(prog)s info my_recording.json               # Show recording information
  %(prog)s list                                 # List all recordings
        """
    )
    
    subparsers = parser.add_subparsers(
        dest='command', help='Available commands'
    )
    
    # Record command
    record_parser = subparsers.add_parser(
        'record', help='Record mouse actions'
    )
    record_parser.add_argument(
        '-o', '--output',
        default='data/mouse_recording.json',
        help='Output file path (default: data/mouse_recording.json)'
    )
    record_parser.set_defaults(func=cmd_record)
    
    # Replay command
    replay_parser = subparsers.add_parser(
        'replay', help='Replay mouse actions'
    )
    replay_parser.add_argument('file', help='Recording file to replay')
    replay_parser.add_argument(
        '-s', '--speed',
        type=float,
        default=1.0,
        help='Replay speed multiplier (default: 1.0)'
    )
    replay_parser.add_argument(
        '-d', '--delay',
        type=int,
        default=3,
        help='Delay in seconds before starting replay (default: 3)'
    )
    replay_parser.set_defaults(func=cmd_replay)
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch GUI interface')
    gui_parser.set_defaults(func=cmd_gui)
    
    # Info command
    info_parser = subparsers.add_parser(
        'info', help='Show recording information'
    )
    info_parser.add_argument('file', help='Recording file to analyze')
    info_parser.set_defaults(func=cmd_info)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all recordings')
    list_parser.add_argument(
        '-d', '--directory',
        default='data',
        help='Directory to search for recordings (default: data)'
    )
    list_parser.set_defaults(func=cmd_list_recordings)
    
    return parser


def interactive_menu():
    """Show interactive menu when no command is provided"""
    show_banner()
    
    while True:
        print("\n🎯 What would you like to do?")
        print("1. 🔴 Record mouse actions")
        print("2. ▶️  Replay recording")
        print("3. 🖥️  Launch GUI interface")
        print("4. 📄 Show recording info")
        print("5. 📁 List recordings")
        print("6. ❓ Show help")
        print("7. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            filename_prompt = ("Enter output filename "
                               "(default: data/mouse_recording.json): ")
            filename = input(filename_prompt).strip()
            if not filename:
                filename = "data/mouse_recording.json"
            
            # Create args object
            class RecordArgs:
                output = filename
            
            result = cmd_record(RecordArgs())
            if result == 0:
                input("\nPress Enter to continue...")
                
        elif choice == '2':
            filename = input("Enter recording filename: ").strip()
            if not filename:
                print("❌ Filename required")
                continue
                
            speed_input = input("Enter replay speed (default: 1.0): ").strip()
            try:
                replay_speed = float(speed_input) if speed_input else 1.0
            except ValueError:
                replay_speed = 1.0
                
            delay_input = input(
                "Enter start delay in seconds (default: 3): "
            ).strip()
            try:
                start_delay = int(delay_input) if delay_input else 3
            except ValueError:
                start_delay = 3
            
            class ReplayArgs:
                file = filename
                speed = replay_speed
                delay = start_delay
                
            result = cmd_replay(ReplayArgs())
            if result == 0:
                input("\nPress Enter to continue...")
                
        elif choice == '3':
            class GuiArgs:
                pass
            cmd_gui(GuiArgs())
            
        elif choice == '4':
            filename = input("Enter recording filename: ").strip()
            if not filename:
                print("❌ Filename required")
                continue
                
            class InfoArgs:
                file = filename
                
            cmd_info(InfoArgs())
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            directory_input = input(
                "Enter directory (default: data): "
            ).strip()
            if not directory_input:
                directory_input = "data"
                
            class ListArgs:
                directory = directory_input
                
            cmd_list_recordings(ListArgs())
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            parser = create_parser()
            parser.print_help()
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")


def main():
    """Main function - entry point for the application"""
    parser = create_parser()
    
    # If no arguments provided, show interactive menu
    if len(sys.argv) == 1:
        interactive_menu()
        return 0
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Show banner for command line usage
    if hasattr(args, 'func'):
        show_banner()
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
