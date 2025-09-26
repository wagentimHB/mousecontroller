# Mouse Recorder & Replayer - Main Entry Point

A comprehensive command-line interface and entry point for the Mouse Recorder & Replayer system.

## Quick Start

### Interactive Mode (Recommended for beginners)
```bash
# Run without arguments for interactive menu
python src/test/main.py

# Or use the root launcher
python mouse_recorder.py
```

### Command Line Mode
```bash
# Record mouse actions
python src/test/main.py record -o my_recording.json

# Replay recording
python src/test/main.py replay my_recording.json

# Launch GUI
python src/test/main.py gui

# Show recording information  
python src/test/main.py info my_recording.json

# List all recordings
python src/test/main.py list
```

## Available Commands

### 🔴 `record` - Record Mouse Actions
Record mouse movements, clicks, and scroll actions.

```bash
python src/test/main.py record [OPTIONS]

Options:
  -o, --output FILE    Output file path (default: data/mouse_recording.json)

Examples:
  python src/test/main.py record                     # Use default filename
  python src/test/main.py record -o session1.json   # Custom filename
```

**During Recording:**
- Move your mouse and perform clicks/scrolls as needed
- Press **ESC** to stop recording
- Recording is automatically saved with metadata

### ▶️ `replay` - Replay Mouse Actions
Replay previously recorded mouse actions with configurable settings.

```bash
python src/test/main.py replay FILE [OPTIONS]

Options:
  -s, --speed FLOAT    Replay speed multiplier (default: 1.0)
  -d, --delay INT      Delay in seconds before starting (default: 3)

Examples:
  python src/test/main.py replay recording.json              # Normal speed
  python src/test/main.py replay recording.json -s 0.5       # Half speed
  python src/test/main.py replay recording.json -s 2 -d 5    # Double speed, 5s delay
```

### 🖥️ `gui` - Launch GUI Interface
Open the PyQt6 graphical user interface for easy recording and replaying.

```bash
python src/test/main.py gui
```

The GUI provides:
- Visual recording controls with status feedback
- Speed slider for replay control (0.1x - 5.0x)
- Progress bars for operations
- File browser for easy file selection
- Settings and configuration options

### 📄 `info` - Show Recording Information
Display detailed information about a recording file.

```bash
python src/test/main.py info FILE

Example:
  python src/test/main.py info my_recording.json
```

Shows:
- Creation date and time
- Recording duration
- Total number of events
- File size
- Event breakdown by type (moves, clicks, scrolls)

### 📁 `list` - List Recordings
List all recording files in a directory with their metadata.

```bash
python src/test/main.py list [OPTIONS]

Options:
  -d, --directory DIR  Directory to search (default: data)

Examples:
  python src/test/main.py list           # List files in data/ directory
  python src/test/main.py list -d /tmp   # List files in custom directory
```

## Interactive Menu

When run without arguments, the program shows an interactive menu:

```
🎯 What would you like to do?
1. 🔴 Record mouse actions
2. ▶️  Replay recording
3. 🖥️  Launch GUI interface
4. 📄 Show recording info
5. 📁 List recordings
6. ❓ Show help
7. 🚪 Exit
```

This is perfect for users who prefer a guided experience over command-line arguments.

## Alternative Launch Methods

### Method 1: Direct Main Module
```bash
python src/test/main.py [COMMAND] [OPTIONS]
```

### Method 2: Root Launcher
```bash
python mouse_recorder.py [COMMAND] [OPTIONS]
```

### Method 3: GUI Only (Windows)
```bash
launch_gui.bat
```

### Method 4: GUI Only (Cross-platform)
```bash
python run_gui.py
```

## Examples Walkthrough

### Example 1: Basic Recording and Replay
```bash
# Step 1: Record a session
python src/test/main.py record -o demo.json

# Step 2: View the recording info
python src/test/main.py info demo.json

# Step 3: Replay at normal speed
python src/test/main.py replay demo.json
```

### Example 2: Advanced Replay Options
```bash
# Record first
python src/test/main.py record -o complex_task.json

# Replay slowly for precision
python src/test/main.py replay complex_task.json -s 0.3 -d 5

# Replay quickly for demo
python src/test/main.py replay complex_task.json -s 3.0 -d 1
```

### Example 3: Managing Multiple Recordings
```bash
# Create several recordings
python src/test/main.py record -o task1.json
python src/test/main.py record -o task2.json
python src/test/main.py record -o task3.json

# List all recordings
python src/test/main.py list

# Get info on specific recording
python src/test/main.py info task2.json
```

## Integration with Other Tools

### Batch Processing
```bash
# Create a batch script to replay multiple recordings
for file in data/*.json; do
    python src/test/main.py replay "$file" -s 2.0
done
```

### Automation Scripts
```python
import subprocess
import sys

# Record via script
result = subprocess.run([
    sys.executable, "src/test/main.py", "record", 
    "-o", "automated_recording.json"
], capture_output=True, text=True)

if result.returncode == 0:
    print("Recording completed successfully")
```

## Error Handling

The main entry point provides comprehensive error handling:

- **File not found**: Clear error messages with file path
- **Permission errors**: Helpful suggestions for resolution
- **Invalid arguments**: Usage examples and suggestions
- **Import errors**: Dependency installation guidance
- **Recording/replay errors**: Detailed error descriptions

## Output Format

### Success Messages
```
✅ Recording completed successfully!
📁 File saved: data/mouse_recording.json
📊 Events recorded: 156
```

### Error Messages
```
❌ Recording file not found: missing.json
❌ Failed to load recording file
⚠️ Recording interrupted by user
```

### Information Display
```
📄 Recording Information: demo.json
----------------------------------------
Created: 2025-09-26 15:30:45
Duration: 12.34 seconds
Total Events: 156
File Size: 2048 bytes

📊 Event Breakdown:
   Move: 120
   Click: 32
   Scroll: 4
```

## Development and Debugging

### Verbose Output
Set environment variable for detailed logging:
```bash
export MOUSE_RECORDER_DEBUG=1
python src/test/main.py record
```

### Module Testing
Test individual components:
```bash
# Test recording module
python -c "from test.mouse_recorder import MouseRecorder; print('Recording module OK')"

# Test replay module  
python -c "from test.mouse_replayer import MouseReplayer; print('Replay module OK')"

# Test GUI module
python -c "from test.mouse_recorder_gui import MouseRecorderGUI; print('GUI module OK')"
```

## Platform-Specific Notes

### Windows
- Use `python` or `py` command
- Batch files (`.bat`) provided for convenience
- GUI works out of the box

### macOS
- May require accessibility permissions for recording
- Use `python3` command if `python` points to Python 2
- GUI requires PyQt6 installation

### Linux
- May need X11 development packages
- Use `python3` command
- Some distributions require additional permissions

## Troubleshooting

### Common Issues

**Command not found:**
```bash
# Make sure you're in the project directory
cd /path/to/mouse_recorder_project
python src/test/main.py --help
```

**Import errors:**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**Permission errors:**
```bash
# On Unix systems, you may need to grant accessibility permissions
# On Windows, run as administrator if needed
```

**GUI won't start:**
```bash
# Install PyQt6
pip install PyQt6

# Test PyQt6 installation
python -c "import PyQt6; print('PyQt6 OK')"
```

---

**Version**: 1.0.0  
**Last Updated**: September 26, 2025  
**Entry Point**: `src/test/main.py`