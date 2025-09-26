#!/usr/bin/env python3
"""
GUI Demo Script - Shows how to launch the GUI
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src" / "test"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def demo_gui():
    """Demo the GUI functionality"""
    print("=" * 60)
    print("MOUSE RECORDER GUI DEMO")
    print("=" * 60)
    
    try:
        from mouse_recorder_gui import MouseRecorderGUI
        from PyQt6.QtWidgets import QApplication
        
        print("✅ Successfully imported GUI components")
        print("✅ PyQt6 is available")
        print("✅ Mouse recorder modules are accessible")
        
        print("\n🚀 GUI Features:")
        print("- 📹 Record mouse movements, clicks, and scrolls")
        print("- ▶️  Replay recordings with adjustable speed")
        print("- 🎛️  Easy-to-use tabbed interface")
        print("- 📊 Progress tracking for replays")
        print("- 💾 File browser for selecting recordings")
        print("- ⚙️  Settings and configuration options")
        
        print("\n📋 How to use:")
        print("1. Run: python run_gui.py")
        print("2. Or double-click: launch_gui.bat")
        print("3. Use the Recording tab to create new recordings")
        print("4. Use the Replay tab to play back recordings")
        print("5. Adjust settings in the Settings tab")
        
        print("\n💡 Tips:")
        print("- Press ESC to stop recording")
        print("- Use speed slider to control replay speed")
        print("- Progress bar shows replay progress")
        print("- All recordings are saved in JSON format")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = demo_gui()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 GUI is ready to use!")
        print("Run 'python run_gui.py' to start the application")
        print("=" * 60)
    else:
        print("\n❌ GUI setup failed. Please check dependencies.")
        sys.exit(1)