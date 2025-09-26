#!/usr/bin/env python3
"""
Mouse Recorder GUI Launcher
Simple script to launch the GUI application via main.py
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import and run the GUI via main entry point
from test.main import cmd_gui

class GuiArgs:
    pass

if __name__ == "__main__":
    print("Starting Mouse Recorder GUI...")
    sys.exit(cmd_gui(GuiArgs()))