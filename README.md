# 🐭 Mouse Recorder & Replayer# 🐭 Mouse Recorder & Replayer



A comprehensive Python application for recording and replaying mouse actions with both command-line and GUI interfaces.A comprehensive Python application for recording and replaying mouse actions with both command-line and GUI interfaces.



![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)## Description

![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)[Add your project description here]

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Installation

## 🌟 Features

1. Clone the repository

### 🎯 **Core Functionality**2. Navigate to the project directory

- **🔴 Record mouse actions** - Capture movements, clicks, and scrolls with precise timing3. Activate the virtual environment:

- **▶️ Replay recordings** - Play back actions with configurable speed and delays   ```bash

- **📊 Progress tracking** - Real-time feedback during recording and replay   # Windows

- **💾 JSON storage** - Human-readable recording format with metadata   venv\Scripts\activate

   

### 🖥️ **User Interfaces**   # macOS/Linux

- **📱 Modern GUI** - PyQt6-based graphical interface with tabbed layout   source venv/bin/activate

- **⌨️ Command-line** - Full CLI with subcommands for automation   ```

- **🎭 Interactive mode** - User-friendly menu system for beginners4. Install dependencies:

- **🚀 Multiple launchers** - Various ways to start the application   ```bash

   pip install -r requirements.txt

### 🎛️ **Advanced Options**   ```

- **⚡ Speed control** - Replay from 0.1x to 5.0x speed

- **⏱️ Timing precision** - Accurate timestamp recording and playback## Development Setup

- **📁 File management** - Browse, analyze, and organize recordings

- **🛡️ Error handling** - Robust error messages and recovery1. Install development dependencies:

   ```bash

## 🚀 Quick Start   pip install -r requirements-dev.txt

   ```

### Installation2. Install pre-commit hooks:

   ```bash

```bash   pre-commit install

# Clone the repository   ```

git clone https://github.com/yourusername/mouse-recorder-replayer.git

cd mouse-recorder-replayer## Usage



# Create virtual environment (recommended)```python

python -m venv venvfrom src.test.main import main



# Activate virtual environmentmain()

# Windows:```

venv\Scripts\activate

# macOS/Linux:Or run directly:

source venv/bin/activate```bash

python src/test/main.py

# Install dependencies```

pip install -r requirements.txt

```## Testing



### Basic UsageRun tests with pytest:

```bash

#### 🎭 Interactive Mode (Beginner-friendly)pytest

```bash```

python mouse_recorder.py

```Run tests with coverage:

```bash

#### ⌨️ Command Line Modepytest --cov=src/test

```bash```

# Record mouse actions

python mouse_recorder.py record -o my_session.json## Project Structure



# Replay recording```

python mouse_recorder.py replay my_session.jsontest/

├── src/

# Launch GUI│   └── test/

python mouse_recorder.py gui│       ├── __init__.py

│       └── main.py

# Show recording info├── tests/

python mouse_recorder.py info my_session.json│   └── __init__.py

├── docs/

# List all recordings├── scripts/

python mouse_recorder.py list├── data/

```├── config/

├── venv/

#### 🖥️ GUI Mode├── requirements.txt

```bash├── requirements-dev.txt

# Method 1: From main launcher├── README.md

python mouse_recorder.py gui├── .gitignore

└── pyproject.toml

# Method 2: Direct GUI launcher```

python run_gui.py

## Contributing

# Method 3: Windows batch file

launch_gui.bat[Add contribution guidelines here]

```

## License

## 📖 Documentation

[Add license information here]

### 📚 Available Guides
- **[Main Entry Point Guide](docs/main_entry_point_guide.md)** - Complete CLI documentation
- **[GUI User Guide](docs/gui_user_guide.md)** - GUI interface documentation
- **[Mouse Recorder Guide](docs/mouse_recorder_guide.md)** - Core functionality guide

### 🎯 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `record` | Record mouse actions | `python mouse_recorder.py record -o session.json` |
| `replay` | Replay recordings | `python mouse_recorder.py replay session.json -s 0.5` |
| `gui` | Launch GUI interface | `python mouse_recorder.py gui` |
| `info` | Show recording details | `python mouse_recorder.py info session.json` |
| `list` | List all recordings | `python mouse_recorder.py list -d data` |

## 🏗️ Project Structure

```
mouse-recorder-replayer/
├── 📁 src/test/                    # Core application modules
│   ├── main.py                     # Main entry point with CLI
│   ├── mouse_recorder.py           # Recording functionality
│   ├── mouse_replayer.py           # Replay functionality
│   ├── mouse_recorder_gui.py       # PyQt6 GUI application
│   └── demo.py                     # Feature demonstration
├── 📁 tests/                       # Test suites
│   ├── test_mouse_recorder.py      # Original tests
│   └── test_mouse_recorder_unittest.py # Unittest framework
├── 📁 docs/                        # Documentation
├── 📁 data/                        # Recording storage
├── 📄 mouse_recorder.py            # Root launcher
├── 📄 run_gui.py                   # GUI launcher
├── 📄 requirements.txt             # Dependencies
└── 📄 README.md                    # This file
```

## 🎮 Usage Examples

### Example 1: Quick Recording
```bash
# Start recording
python mouse_recorder.py record -o demo.json
# Move mouse, click around, press ESC when done

# Replay at half speed  
python mouse_recorder.py replay demo.json -s 0.5
```

### Example 2: GUI Workflow
```bash
# Launch GUI
python mouse_recorder.py gui
# Use Recording tab → Replay tab with speed control
```

## 🐛 Troubleshooting

**GUI won't start:**
```bash
pip install PyQt6
```

**Recording doesn't work:**
- Windows: Run as administrator if needed
- macOS: Grant accessibility permissions
- Linux: Install X11 development packages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

---

**🐭 Mouse Recorder & Replayer** - Making mouse automation simple and powerful!

**Version**: 1.0.0 | **Python**: 3.8+