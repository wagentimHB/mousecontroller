# Mouse Recorder GUI

A modern, user-friendly graphical interface for recording and replaying mouse actions built with PyQt6.

![GUI Screenshot](docs/gui_preview.png)

## Features

### 🎯 **Recording Features**
- **Real-time mouse tracking** - Records all mouse movements with precise coordinates
- **Click detection** - Captures left, right, and middle mouse button actions
- **Scroll recording** - Records mouse wheel movements (horizontal and vertical)
- **ESC to stop** - Simple keyboard shortcut to end recording
- **File management** - Easy file selection with browse dialog
- **Live status updates** - Real-time feedback during recording

### 🎬 **Replay Features**
- **Speed control** - Adjust playback speed from 0.1x to 5.0x using a slider
- **Start delay** - Configurable countdown (0-10 seconds) before replay begins
- **Progress tracking** - Visual progress bar during replay
- **One-click replay** - Simple button to start playback
- **File validation** - Automatic checking of recording files before replay

### 💻 **User Interface**
- **Tabbed interface** - Organized into Recording, Replay, and Settings tabs
- **Modern design** - Clean, professional appearance with intuitive controls
- **Status messages** - Clear feedback in status bar and labels
- **Error handling** - User-friendly error messages and warnings
- **File information** - Detailed metadata display for recordings

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Quick Setup
```bash
# Clone or navigate to the project directory
cd C:/workspaces/python_projects/test

# Activate virtual environment (if using one)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch GUI
python run_gui.py
```

### Alternative Launch Methods
```bash
# Method 1: Direct Python execution
python run_gui.py

# Method 2: Windows batch file
launch_gui.bat

# Method 3: Run from src directory
python src/test/mouse_recorder_gui.py
```

## How to Use

### 🔴 **Recording Tab**
1. **Set filename**: Enter or browse for output file location
2. **Start recording**: Click "Start Recording" button
3. **Perform actions**: Move mouse, click, and scroll as needed
4. **Stop recording**: Press **ESC** key to finish
5. **View results**: Recording information will be displayed automatically

### ▶️ **Replay Tab**
1. **Select file**: Browse or enter path to recording file
2. **Adjust settings**:
   - **Speed**: Use slider to control playback speed (0.1x - 5.0x)
   - **Delay**: Set countdown time before replay starts (0-10 seconds)
3. **Start replay**: Click "Start Replay" button
4. **Monitor progress**: Watch progress bar and status updates
5. **Stop if needed**: Click "Stop Replay" to interrupt

### ⚙️ **Settings Tab**
- **Default directory**: Configure default save location
- **Auto-load**: Automatically load last recording for replay
- **About information**: View application details and version

## File Format

Recordings are saved in JSON format with this structure:

```json
{
  "metadata": {
    "created_at": "2025-09-26T15:30:45.123456",
    "duration": 12.34,
    "event_count": 156
  },
  "events": [
    {
      "type": "move",
      "x": 100,
      "y": 200,
      "timestamp": 0.125
    },
    {
      "type": "click", 
      "x": 150,
      "y": 250,
      "button": "left",
      "pressed": true,
      "timestamp": 1.567
    }
  ]
}
```

## GUI Components

### Main Window
- **Tabbed interface** with three main sections
- **Status bar** for real-time feedback
- **Menu system** (planned for future versions)
- **Responsive layout** that adapts to window size

### Recording Controls
- **File input** with browse button
- **Start/Stop buttons** with visual feedback
- **Status display** showing current recording state
- **Information panel** with file details

### Replay Controls
- **File selection** with validation
- **Speed slider** with live value display
- **Delay spinbox** for start countdown
- **Progress bar** during replay
- **Control buttons** for start/stop operations

## Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|---------|---------|
| **ESC** | Stop recording | During recording |
| **Ctrl+C** | Stop replay | During replay |
| **Ctrl+Q** | Quit application | Anytime |

## Technical Details

### Architecture
- **PyQt6** for GUI framework
- **Threading** for non-blocking recording/replay
- **Signal/Slot system** for event handling
- **Error handling** with user-friendly messages

### Performance
- **Minimal CPU usage** during recording
- **Efficient memory management** for large recordings
- **Smooth playback** with accurate timing
- **Responsive UI** that doesn't freeze during operations

### Compatibility
- **Windows 10/11** (fully tested)
- **macOS** (with accessibility permissions)
- **Linux** (with X11 support)

## Troubleshooting

### Common Issues

**GUI won't start:**
```bash
# Check PyQt6 installation
python -c "import PyQt6; print('PyQt6 OK')"

# Reinstall if needed
pip install --upgrade PyQt6
```

**Recording doesn't work:**
- Ensure pynput has proper permissions
- On macOS: Grant accessibility permissions
- On Linux: Install X11 development packages

**Replay actions in wrong locations:**
- Check screen resolution matches recording conditions
- Ensure window positions are similar to recording time
- Use slower speeds for more precise positioning

**File errors:**
- Verify file path permissions
- Check disk space for recordings
- Ensure JSON file format is valid

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "No recording file selected" | Empty file path | Browse and select a valid file |
| "File does not exist" | Invalid file path | Check file location and spelling |
| "Failed to load recording" | Corrupted JSON | Re-record or use backup file |
| "Recording failed" | Permission issues | Run as administrator or check permissions |

## Advanced Usage

### Batch Processing
```python
# Example: Convert multiple recordings
from src.test.mouse_recorder_gui import MouseRecorderGUI
# Custom scripting possible through direct class access
```

### Custom Speeds
- **0.1x**: Ultra-slow for precise operations
- **0.5x**: Half-speed for careful positioning  
- **1.0x**: Original recording speed
- **2.0x**: Double-speed for demonstrations
- **5.0x**: Maximum speed for quick playback

### Integration
The GUI can be integrated into other applications:
```python
from src.test.mouse_recorder_gui import MouseRecorderGUI
# Embed in larger applications or automation suites
```

## Development

### Project Structure
```
src/test/
├── mouse_recorder_gui.py      # Main GUI application
├── mouse_recorder.py          # Recording backend
├── mouse_replayer.py          # Replay backend
└── __init__.py               # Package initialization

scripts/
├── run_gui.py                # GUI launcher
├── launch_gui.bat            # Windows batch launcher
└── demo_gui.py              # Feature demonstration
```

### Contributing
1. Fork the repository
2. Create feature branch
3. Test GUI functionality thoroughly
4. Submit pull request with screenshots

### Future Enhancements
- [ ] Recording regions (partial screen recording)
- [ ] Keyboard shortcut recording
- [ ] Recording scheduling and automation
- [ ] Export to different formats
- [ ] Macro recording capabilities
- [ ] Network-based recording sharing

## License

This project is part of the Mouse Recorder & Replayer suite.
See main project documentation for license details.

---

**Version**: 1.0.0  
**Last Updated**: September 26, 2025  
**Built with**: Python, PyQt6, pynput