#!/usr/bin/env python3
"""
Mouse Recorder Main Launcher
Launches the main entry point from the project root
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import and run main
from test.main import main

if __name__ == "__main__":
    sys.exit(main())