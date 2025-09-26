#!/usr/bin/env python3
"""
Mouse Recorder GUI Launcher
Simple script to launch the GUI application via main.py
"""

import sys
from pathlib import Path


def main():
    """Main function to launch the GUI application"""
    print("Starting Mouse Recorder GUI...")
    
    # Add src to path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    try:
        # Import and run the GUI via main entry point
        from mousecontroller.main import cmd_gui
         
        class GuiArgs:
            pass

        return cmd_gui(GuiArgs())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
