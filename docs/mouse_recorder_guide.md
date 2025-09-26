# Mouse Recorder and Replayer

This project provides tools to record and replay mouse movements, clicks, and scroll actions on your computer.

## Features

- **Record mouse movements**: Captures all mouse position changes
- **Record mouse clicks**: Captures left, right, and middle mouse button presses and releases
- **Record mouse scrolling**: Captures scroll wheel movements
- **Save to JSON**: Recordings are saved in a structured JSON format
- **Replay recordings**: Play back recorded mouse actions with configurable speed
- **Interactive interface**: Easy-to-use command-line interface

## Requirements

- Python 3.6+
- `pynput` library (automatically installed)

## Installation

The required dependencies are already installed in your virtual environment:
- `pynput` - for capturing and controlling mouse events

## Usage

### 1. Recording Mouse Actions

Run the mouse recorder:

```bash
python src/mousecontroller/mouse_recorder.py
```

Or specify a custom output file:

```bash
python src/mousecontroller/mouse_recorder.py data/my_recording.json
```

**How to record:**
1. Run the script
2. Move your mouse around and click where needed
3. Press **ESC** to stop recording
4. The recording will be saved to `data/mouse_recording.json` (or your specified file)

### 2. Replaying Mouse Actions

Run the mouse replayer:

```bash
python src/mousecontroller/mouse_replayer.py
```

Or specify a custom recording file:

```bash
python src/mousecontroller/mouse_replayer.py data/my_recording.json
```

**Replay options:**
- Normal speed (1x)
- Half speed (0.5x) - for precise movements
- Double speed (2x) - for faster replay
- Custom speed - any positive number
- Load different recording files

### 3. Demo Script

For a guided experience, run the demo:

```bash
python src/mousecontroller/demo.py
```

This provides an interactive menu to try both recording and replaying.

## File Structure

```
src/mousecontroller/
├── mouse_recorder.py    # Main recording script
├── mouse_replayer.py    # Main replay script
├── demo.py             # Interactive demo
└── __init__.py

data/
└── mouse_recording.json # Default recording file (created after first recording)
```

## Recording File Format

Recordings are saved in JSON format with the following structure:

```json
{
  "metadata": {
    "created_at": "2025-09-26T10:30:45.123456",
    "duration": 15.67,
    "event_count": 245
  },
  "events": [
    {
      "type": "move",
      "x": 100,
      "y": 200,
      "timestamp": 0.001
    },
    {
      "type": "click",
      "x": 150,
      "y": 250,
      "button": "left",
      "pressed": true,
      "timestamp": 1.234
    },
    {
      "type": "scroll",
      "x": 200,
      "y": 300,
      "dx": 0,
      "dy": -1,
      "timestamp": 2.567
    }
  ]
}
```

## Event Types

1. **move**: Mouse position changes
   - `x`, `y`: Screen coordinates
   - `timestamp`: Time from start of recording

2. **click**: Mouse button actions
   - `x`, `y`: Click position
   - `button`: "left", "right", or "middle"
   - `pressed`: true for press, false for release
   - `timestamp`: Time from start of recording

3. **scroll**: Mouse wheel actions
   - `x`, `y`: Scroll position
   - `dx`, `dy`: Scroll deltas (horizontal/vertical)
   - `timestamp`: Time from start of recording

## Tips

### Recording Tips
- Keep movements smooth for better replay quality
- Avoid extremely fast movements that might be hard to replay accurately
- Make sure to record complete click actions (both press and release)
- Press ESC when you're completely done with your sequence

### Replay Tips
- Make sure your screen resolution and window positions match the recording conditions
- Use slower speeds (0.5x) for precise operations
- Use faster speeds (2x+) for quick demonstrations
- Position your mouse cursor appropriately before starting replay
- Keep other applications' windows in similar positions as during recording

## Troubleshooting

### Common Issues

1. **"Permission denied" errors on macOS/Linux**: You may need to grant accessibility permissions to your terminal or Python interpreter.

2. **Replay actions happening in wrong locations**: Make sure your screen resolution and window positions match those during recording.

3. **Recording stops immediately**: Check that pynput is properly installed and has the necessary permissions.

4. **ESC key not stopping recording**: Make sure the terminal window has focus when pressing ESC.

### Platform Notes

- **Windows**: Should work out of the box
- **macOS**: May require accessibility permissions
- **Linux**: May require X11 development packages

## Safety Notes

- Be careful when replaying recordings, as they will perform actual mouse actions
- Always review recordings before replaying them
- Use the 3-second delay before replay to position yourself appropriately
- You can interrupt replay with Ctrl+C
- Test recordings with simple movements first

## Examples

### Example 1: Record a simple sequence
```bash
# Start recording
python src/mousecontroller/mouse_recorder.py

# Move mouse, click a few times, then press ESC
# Recording saved to data/mouse_recording.json
```

### Example 2: Replay at half speed
```bash
# Replay with interactive menu
python src/mousecontroller/mouse_replayer.py
# Choose option 2 for half speed
```

### Example 3: Command line replay
```bash
# Direct replay at double speed
python src/mousecontroller/mouse_replayer.py data/mouse_recording.json 2.0
```
