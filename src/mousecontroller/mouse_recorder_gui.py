#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mouse Recorder GUI Application using PyQt6
Provides an easy-to-use interface for recording and replaying mouse actions
"""

import sys
import os
import json
import time
import threading
import importlib.util
from pathlib import Path
from typing import Any, Union
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, QSlider,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox, QProgressBar,
    QCheckBox, QTabWidget
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src" / "mousecontroller"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# Import modules dynamically to avoid linting issues
def import_module_from_path(
    module_name: str, file_path: Union[str, Path]
) -> Any:
    """Import a module from a specific file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import our modules
try:
    current_dir = Path(__file__).parent
    mouse_recorder_module = import_module_from_path(
        "mouse_recorder", current_dir / "mouse_recorder.py"
    )
    mouse_replayer_module = import_module_from_path(
        "mouse_replayer", current_dir / "mouse_replayer.py"
    )
    MouseRecorder = mouse_recorder_module.MouseRecorder
    MouseReplayer = mouse_replayer_module.MouseReplayer
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)


class RecorderThread(QThread):
    """Thread for handling mouse recording"""
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str, int)  # filename, event_count
    recording_error = pyqtSignal(str)
    timer_update = pyqtSignal(str)  # timer display string
    status_blink = pyqtSignal(bool)  # blinking status indicator
    
    def __init__(self, output_file: str) -> None:
        super().__init__()
        self.output_file = output_file
        self.recorder = None
        
    def run(self) -> None:
        try:
            # Create a custom recorder that supports GUI timer updates
            self.recorder = self._create_gui_recorder(self.output_file)
            self.recording_started.emit()
            self.recorder.start_recording()
            # Recording stops when ESC is pressed
            event_count = (
                len(self.recorder.events) if self.recorder.events else 0
            )
            self.recording_stopped.emit(self.output_file, event_count)
        except Exception as e:
            self.recording_error.emit(str(e))
    
    def _create_gui_recorder(self, output_file: str) -> Any:
        """Create a MouseRecorder with GUI timer updates"""
        recorder = MouseRecorder(output_file)
        
        # Import mouse from pynput for listener
        from pynput import mouse
        
        # Override the start_recording method to not print console messages
        def gui_start_recording():
            recorder.recording = True
            recorder.start_time = time.time()
            recorder.events = []
            recorder.timer_stop_event.clear()
            
            # Start timer display thread (GUI version)
            recorder.timer_thread = threading.Thread(target=gui_display_timer)
            recorder.timer_thread.daemon = True
            recorder.timer_thread.start()
            
            # Start mouse listener
            recorder.listener = mouse.Listener(
                on_move=recorder.on_move,
                on_click=recorder.on_click,
                on_scroll=recorder.on_scroll
            )
            
            recorder.listener.start()
            
            # Monitor for ESC key to stop recording
            recorder._monitor_stop_key()
        
        # Override the _display_timer method to emit GUI updates
        def gui_display_timer():
            blink_counter = 0
            while not recorder.timer_stop_event.is_set():
                if recorder.recording and recorder.start_time > 0:
                    elapsed = time.time() - recorder.start_time
                    time_str = recorder._format_time(elapsed)
                    # Emit just the time string for GUI display
                    self.timer_update.emit(time_str)
                    
                    # Emit blinking status every 10 cycles (1 second)
                    blink_counter += 1
                    if blink_counter >= 10:
                        self.status_blink.emit(True)
                        blink_counter = 0
                    elif blink_counter == 5:
                        self.status_blink.emit(False)
                
                # Update every 0.1 seconds for smooth display
                recorder.timer_stop_event.wait(0.1)
        
        # Override methods that print to console
        recorder.start_recording = gui_start_recording
        recorder._display_timer = gui_display_timer
        
        return recorder
    
    def stop_recording(self) -> None:
        """Stop recording by simulating ESC key press - same as manual ESC"""
        if self.recorder and self.recorder.recording:
            try:
                # Import pynput to simulate ESC key press
                from pynput.keyboard import Key, Controller
                
                # Create keyboard controller and send ESC key
                keyboard_controller = Controller()
                keyboard_controller.press(Key.esc)
                keyboard_controller.release(Key.esc)
                
            except ImportError:
                # Fallback to direct stop if pynput not available
                self.recorder.stop_recording()
            except Exception as e:
                # Fallback to direct stop if any error occurs
                print(f"Error simulating ESC key: {e}")
                self.recorder.stop_recording()


class ReplayThread(QThread):
    """Thread for handling mouse replay"""
    replay_started = pyqtSignal()
    replay_progress = pyqtSignal(int)  # percentage
    replay_finished = pyqtSignal()
    replay_error = pyqtSignal(str)
    replay_count_update = pyqtSignal(int, int)  # current, total
    
    def __init__(self, recording_file, speed=1.0, delay_start=3,
                 replay_times=1, replay_hours=0.0, replay_latency=2.0):
        super().__init__()
        self.recording_file = recording_file
        self.speed = speed
        self.delay_start = delay_start
        self.replay_times = replay_times
        self.replay_hours = float(replay_hours)  # Hours for time-based replay
        self.replay_latency = float(replay_latency)  # Pause between replays
        self.replayer = None
        
    def run(self):
        try:
            self.replayer = MouseReplayer(self.recording_file)
            if not self.replayer.load_recording():
                self.replay_error.emit("Failed to load recording file")
                return
                
            # Configure replay settings
            self.replayer.set_replay_times(self.replay_times)
            self.replayer.set_replay_hours(self.replay_hours)
            self.replayer.set_replay_latency(self.replay_latency)
                
            self.replay_started.emit()
            
            # Custom replay with progress updates
            if not self.replayer.recording_data:
                self.replay_error.emit("No recording data available")
                return
                
            events = self.replayer.recording_data['events']
            if not events:
                self.replay_error.emit("No events to replay")
                return
            
            # Countdown delay
            for i in range(self.delay_start, 0, -1):
                time.sleep(1)
            
            # Time-based or count-based replay
            if self.replay_hours > 0:
                self._time_based_replay(events)
            else:
                self._count_based_replay(events)
                
            self.replay_finished.emit()
            
        except Exception as e:
            self.replay_error.emit(str(e))
    
    def _time_based_replay(self, events):
        """Execute time-based replay for specified hours"""
        end_time = time.time() + (self.replay_hours * 3600)
        replay_count = 0
        
        while time.time() < end_time and self.isRunning():
            replay_count += 1
            remaining_time = end_time - time.time()
            
            # -1 indicates time-based replay mode
            self.replay_count_update.emit(replay_count, -1)
            
            # Check if we have enough time for complete replay
            metadata = self.replayer.recording_data['metadata']
            recording_duration = metadata['duration'] / self.speed
            if remaining_time < recording_duration:
                break
            
            # Execute single replay
            start_time = time.time()
            for i, event in enumerate(events):
                if not self.isRunning() or time.time() >= end_time:
                    return
                    
                # Calculate delay based on timestamp and replay speed
                target_time = event['timestamp'] / self.speed
                current_elapsed = time.time() - start_time
                delay = target_time - current_elapsed
                
                if delay > 0:
                    time.sleep(delay)
                    
                self.replayer._execute_event(event)
                
                # Update progress based on time remaining
                start_time = end_time - self.replay_hours * 3600
                elapsed_time = time.time() - start_time
                total_time = self.replay_hours * 3600
                time_progress = int((elapsed_time / total_time) * 100)
                self.replay_progress.emit(min(time_progress, 100))
            
            # Configurable pause between replays
            if time.time() < end_time and self.isRunning():
                if self.replay_latency > 0:
                    time.sleep(self.replay_latency)
    
    def _count_based_replay(self, events):
        """Execute count-based replay for specified number of times"""
        # Multiple replay loop
        for replay_num in range(self.replay_times):
            if not self.isRunning():  # Check if thread should stop
                break
            
            self.replay_count_update.emit(replay_num + 1, self.replay_times)
            
            start_time = time.time()
            
            for i, event in enumerate(events):
                if not self.isRunning():  # Check if thread should stop
                    break
                    
                # Calculate delay based on timestamp and replay speed
                target_time = event['timestamp'] / self.speed
                current_elapsed = time.time() - start_time
                delay = target_time - current_elapsed
                
                if delay > 0:
                    time.sleep(delay)
                    
                self.replayer._execute_event(event)
                
                # Update progress for current replay
                event_progress = int((i / len(events)) * 100)
                # Calculate overall progress across all replays
                overall_progress = int(
                    ((replay_num * 100) + event_progress) / self.replay_times
                )
                self.replay_progress.emit(overall_progress)
            
            # Add configurable pause between replays (except for last one)
            if replay_num < self.replay_times - 1 and self.isRunning():
                if self.replay_latency > 0:
                    time.sleep(self.replay_latency)


class MouseRecorderGUI(QMainWindow):
    """Main GUI application for mouse recording and replay"""
    
    def __init__(self):
        super().__init__()
        self.recorder_thread = None
        self.replay_thread = None
        self.current_recording_file = "data/mouse_recording.json"
        
        self.init_ui()
        self.setup_connections()
        self.update_file_info()
        
    def safe_status_message(self, message: str):
        """Safely update status bar message"""
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage(message)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Mouse Recorder & Replayer")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application icon and style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            .record-button {
                background-color: #ff4444;
            }
            .record-button:hover {
                background-color: #cc3333;
            }
            .stop-button {
                background-color: #ff8800;
            }
            .stop-button:hover {
                background-color: #cc6600;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_recording_tab()
        self.create_replay_tab()
        self.create_settings_tab()
        
        # Status bar
        self.safe_status_message("Ready")
        
    def create_recording_tab(self):
        """Create the recording tab"""
        recording_widget = QWidget()
        layout = QVBoxLayout(recording_widget)
        
        # File selection group
        file_group = QGroupBox("Recording File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_input = QLineEdit(self.current_recording_file)
        self.file_input.setPlaceholderText("Enter recording file path...")
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_recording_file)
        
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_button)
        
        # Recording controls group
        controls_group = QGroupBox("Recording Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Start recording button
        self.start_record_button = QPushButton("🔴 Start Recording")
        self.start_record_button.setProperty("class", "record-button")
        self.start_record_button.setStyleSheet("background-color: #ff4444;")
        self.start_record_button.clicked.connect(self.start_recording)
        
        # Stop recording button
        self.stop_record_button = QPushButton("⏹️ Stop Recording")
        self.stop_record_button.setProperty("class", "stop-button")
        self.stop_record_button.setStyleSheet("background-color: #ff8800;")
        self.stop_record_button.setEnabled(False)
        self.stop_record_button.clicked.connect(self.stop_recording)
        
        # Recording status
        self.recording_status = QLabel("Status: Ready to record")
        self.recording_status.setStyleSheet("font-size: 14px; color: #333;")
        
        # Recording timer container with dedicated design
        self.timer_container = QGroupBox("Recording Timer")
        self.timer_container.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #666;
            }
        """)
        self.timer_container.hide()  # Initially hidden
        
        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setSpacing(5)
        
        # Main timer display
        self.recording_timer = QLabel("00:00:00")
        self.recording_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_display_style = """
            QLabel {
                font-family: 'Courier New', monospace;
                font-size: 32px;
                font-weight: bold;
                color: #dc3545;
                background-color: #000;
                border: 3px solid #333;
                border-radius: 8px;
                padding: 10px 20px;
                margin: 5px;
            }
        """
        self.recording_timer.setStyleSheet(timer_display_style)
        
        # Timer status label
        self.timer_status = QLabel("● RECORDING")
        self.timer_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_status.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #dc3545;
                background-color: transparent;
                padding: 5px;
            }
        """)
        
        timer_layout.addWidget(self.recording_timer)
        timer_layout.addWidget(self.timer_status)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_record_button)
        button_layout.addWidget(self.stop_record_button)
        
        controls_layout.addLayout(button_layout)
        controls_layout.addWidget(self.recording_status)
        controls_layout.addWidget(self.timer_container)
        
        # Recording info group
        info_group = QGroupBox("Recording Information")
        info_layout = QVBoxLayout(info_group)
        
        self.recording_info = QTextEdit()
        self.recording_info.setReadOnly(True)
        self.recording_info.setMaximumHeight(150)
        self.recording_info.setPlainText("No recording information available.")
        
        info_layout.addWidget(self.recording_info)
        
        # Instructions group
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QLabel("""
        📋 How to Record:
        1. Choose or enter a file path for saving the recording
        2. Click "Start Recording" button
        3. Move your mouse and click where needed
        4. Press ESC key to stop recording
        5. The recording will be automatically saved
        
        ⚠️ Note: The recording captures all mouse movements,
        clicks, and scrolls
        """)
        instructions_text.setWordWrap(True)
        instructions_text.setStyleSheet("color: #666; font-size: 12px;")
        
        instructions_layout.addWidget(instructions_text)
        
        # Add all groups to layout
        layout.addWidget(file_group)
        layout.addWidget(controls_group)
        layout.addWidget(info_group)
        layout.addWidget(instructions_group)
        layout.addStretch()
        
        self.tab_widget.addTab(recording_widget, "🔴 Recording")
        
    def create_replay_tab(self):
        """Create the replay tab"""
        replay_widget = QWidget()
        layout = QVBoxLayout(replay_widget)
        
        # File selection group
        file_group = QGroupBox("Replay File")
        file_layout = QHBoxLayout(file_group)
        
        self.replay_file_input = QLineEdit(self.current_recording_file)
        self.replay_file_input.setPlaceholderText(
            "Enter recording file to replay..."
        )
        
        self.replay_browse_button = QPushButton("Browse...")
        self.replay_browse_button.clicked.connect(self.browse_replay_file)
        
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.replay_file_input)
        file_layout.addWidget(self.replay_browse_button)
        
        # Replay settings group
        settings_group = QGroupBox("Replay Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(10)  # 0.1x speed
        self.speed_slider.setMaximum(500)  # 5.0x speed
        self.speed_slider.setValue(100)    # 1.0x speed
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(50)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setMinimumWidth(40)
        
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        
        # Delay control
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Start Delay:"))
        
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(0)
        self.delay_spinbox.setMaximum(10)
        self.delay_spinbox.setValue(3)
        self.delay_spinbox.setSuffix(" seconds")
        
        delay_layout.addWidget(self.delay_spinbox)
        delay_layout.addStretch()
        
        # Replay times control
        times_layout = QHBoxLayout()
        times_layout.addWidget(QLabel("Replay Times:"))
        
        self.replay_times_spinbox = QSpinBox()
        self.replay_times_spinbox.setMinimum(1)
        self.replay_times_spinbox.setMaximum(100)
        self.replay_times_spinbox.setValue(1)
        self.replay_times_spinbox.setSuffix(" time(s)")
        
        times_layout.addWidget(self.replay_times_spinbox)
        times_layout.addStretch()
        
        # Replay hours control
        hours_layout = QHBoxLayout()
        hours_layout.addWidget(QLabel("Replay Hours:"))
        
        self.replay_hours_spinbox = QSpinBox()
        self.replay_hours_spinbox.setMinimum(0)
        self.replay_hours_spinbox.setMaximum(240)  # Max 10 days
        self.replay_hours_spinbox.setValue(0)
        self.replay_hours_spinbox.setSuffix(" hour(s)")
        self.replay_hours_spinbox.setSpecialValueText("Disabled")
        
        hours_layout.addWidget(self.replay_hours_spinbox)
        
        # Minutes spinbox for more precise control
        self.replay_minutes_spinbox = QSpinBox()
        self.replay_minutes_spinbox.setMinimum(0)
        self.replay_minutes_spinbox.setMaximum(59)
        self.replay_minutes_spinbox.setValue(0)
        self.replay_minutes_spinbox.setSuffix(" min")
        
        hours_layout.addWidget(QLabel(":"))
        hours_layout.addWidget(self.replay_minutes_spinbox)
        hours_layout.addStretch()
        
        # Latency control
        latency_layout = QHBoxLayout()
        latency_layout.addWidget(QLabel("Pause between replays:"))
        
        self.replay_latency_spinbox = QDoubleSpinBox()
        self.replay_latency_spinbox.setMinimum(0.0)
        self.replay_latency_spinbox.setMaximum(60.0)
        self.replay_latency_spinbox.setValue(2.0)
        self.replay_latency_spinbox.setSingleStep(0.5)
        self.replay_latency_spinbox.setDecimals(1)
        self.replay_latency_spinbox.setSuffix(" sec")
        self.replay_latency_spinbox.setSpecialValueText("No pause")
        
        latency_layout.addWidget(self.replay_latency_spinbox)
        latency_layout.addStretch()
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        
        self.count_mode_radio = QCheckBox("Count-based (use replay times)")
        self.time_mode_radio = QCheckBox("Time-based (use replay hours)")
        self.count_mode_radio.setChecked(True)
        
        # Connect radio buttons for exclusive selection
        self.count_mode_radio.toggled.connect(self.on_mode_changed)
        self.time_mode_radio.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.count_mode_radio)
        mode_layout.addWidget(self.time_mode_radio)
        mode_layout.addStretch()
        
        settings_layout.addLayout(speed_layout)
        settings_layout.addLayout(delay_layout)
        settings_layout.addLayout(times_layout)
        settings_layout.addLayout(hours_layout)
        settings_layout.addLayout(latency_layout)
        settings_layout.addLayout(mode_layout)
        
        # Replay controls group
        controls_group = QGroupBox("Replay Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Start replay button
        self.start_replay_button = QPushButton("▶️ Start Replay")
        self.start_replay_button.setStyleSheet("background-color: #4CAF50;")
        self.start_replay_button.clicked.connect(self.start_replay)
        
        # Stop replay button
        self.stop_replay_button = QPushButton("⏹️ Stop Replay")
        self.stop_replay_button.setStyleSheet("background-color: #ff8800;")
        self.stop_replay_button.setEnabled(False)
        self.stop_replay_button.clicked.connect(self.stop_replay)
        
        # Replay progress
        self.replay_progress_bar = QProgressBar()
        self.replay_progress_bar.setVisible(False)
        
        # Replay status
        self.replay_status = QLabel("Status: Ready to replay")
        self.replay_status.setStyleSheet("font-size: 14px; color: #333;")
        
        # Replay count status
        self.replay_count_status = QLabel("")
        self.replay_count_status.setStyleSheet("font-size: 12px; color: #666;")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_replay_button)
        button_layout.addWidget(self.stop_replay_button)
        
        controls_layout.addLayout(button_layout)
        controls_layout.addWidget(self.replay_progress_bar)
        controls_layout.addWidget(self.replay_status)
        controls_layout.addWidget(self.replay_count_status)
        
        # File info group
        replay_info_group = QGroupBox("Replay File Information")
        replay_info_layout = QVBoxLayout(replay_info_group)
        
        self.replay_info = QTextEdit()
        self.replay_info.setReadOnly(True)
        self.replay_info.setMaximumHeight(120)
        self.replay_info.setPlainText("No file loaded.")
        
        replay_info_layout.addWidget(self.replay_info)
        
        # Add all groups to layout
        layout.addWidget(file_group)
        layout.addWidget(settings_group)
        layout.addWidget(controls_group)
        layout.addWidget(replay_info_group)
        layout.addStretch()
        
        self.tab_widget.addTab(replay_widget, "▶️ Replay")
        
    def create_settings_tab(self):
        """Create the settings tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)
        
        # Default directory
        self.default_dir_checkbox = QCheckBox("Use default data directory")
        self.default_dir_checkbox.setChecked(True)
        
        # Auto-load last file
        self.auto_load_checkbox = QCheckBox("Auto-load last recording file")
        self.auto_load_checkbox.setChecked(True)
        
        general_layout.addWidget(self.default_dir_checkbox)
        general_layout.addWidget(self.auto_load_checkbox)
        
        # About group
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)
        
        about_text = QLabel("""
        <h3>Mouse Recorder & Replayer</h3>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> A GUI application for recording and
        replaying mouse actions</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Record mouse movements, clicks, and scrolls</li>
        <li>Replay recordings at different speeds</li>
        <li>Save recordings in JSON format</li>
        <li>Easy-to-use graphical interface</li>
        </ul>
        <p><b>Built with:</b> Python, PyQt6, pynput</p>
        """)
        about_text.setWordWrap(True)
        
        about_layout.addWidget(about_text)
        
        layout.addWidget(general_group)
        layout.addWidget(about_group)
        layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
        
    def setup_connections(self):
        """Setup signal connections"""
        # File input connections
        self.file_input.textChanged.connect(self.on_recording_file_changed)
        self.replay_file_input.textChanged.connect(self.on_replay_file_changed)
        
    def browse_recording_file(self):
        """Browse for recording file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recording As",
            self.current_recording_file,
            "JSON files (*.json);;All files (*.*)"
        )
        if filename:
            self.file_input.setText(filename)
            self.current_recording_file = filename
            
    def browse_replay_file(self):
        """Browse for replay file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Recording File",
            self.current_recording_file,
            "JSON files (*.json);;All files (*.*)"
        )
        if filename:
            self.replay_file_input.setText(filename)
            self.update_replay_file_info(filename)
            
    def on_recording_file_changed(self, filename):
        """Handle recording file change"""
        self.current_recording_file = filename
        self.update_file_info()
        
    def on_replay_file_changed(self, filename):
        """Handle replay file change"""
        self.update_replay_file_info(filename)
        
    def on_mode_changed(self):
        """Handle mode selection change"""
        if self.count_mode_radio.isChecked():
            self.time_mode_radio.setChecked(False)
            self.replay_times_spinbox.setEnabled(True)
            self.replay_hours_spinbox.setEnabled(False)
            self.replay_minutes_spinbox.setEnabled(False)
        else:
            self.count_mode_radio.setChecked(False)
            self.replay_times_spinbox.setEnabled(False)
            self.replay_hours_spinbox.setEnabled(True)
            self.replay_minutes_spinbox.setEnabled(True)
            
    def update_speed_label(self, value):
        """Update speed label"""
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        
    def update_file_info(self):
        """Update recording file information"""
        filename = self.current_recording_file
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    
                    info = f"""File: {filename}
Created: {metadata.get('created_at', 'Unknown')}
Duration: {metadata.get('duration', 0):.2f} seconds
Events: {metadata.get('event_count', 0)}
File Size: {os.path.getsize(filename)} bytes"""
                    
                    self.recording_info.setPlainText(info)
            except Exception as e:
                self.recording_info.setPlainText(f"Error reading file: {e}")
        else:
            error_msg = f"File does not exist: {filename}"
            self.recording_info.setPlainText(error_msg)
            
    def update_replay_file_info(self, filename):
        """Update replay file information"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    
                    info = f"""File: {filename}
Created: {metadata.get('created_at', 'Unknown')}
Duration: {metadata.get('duration', 0):.2f} seconds
Events: {metadata.get('event_count', 0)}
File Size: {os.path.getsize(filename)} bytes

Ready to replay!"""
                    
                    self.replay_info.setPlainText(info)
            except Exception as e:
                self.replay_info.setPlainText(f"Error reading file: {e}")
        else:
            self.replay_info.setPlainText(f"File does not exist: {filename}")
            
    def start_recording(self):
        """Start mouse recording"""
        filename = self.file_input.text().strip()
        if not filename:
            QMessageBox.warning(
                self, "Warning",
                "Please enter a filename for the recording."
            )
            return
            
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Start recording thread
        self.recorder_thread = RecorderThread(filename)
        self.recorder_thread.recording_started.connect(
            self.on_recording_started)
        self.recorder_thread.recording_stopped.connect(
            self.on_recording_stopped)
        self.recorder_thread.recording_error.connect(self.on_recording_error)
        self.recorder_thread.timer_update.connect(self.on_timer_update)
        self.recorder_thread.status_blink.connect(self.on_status_blink)
        
        self.recorder_thread.start()
        
    def stop_recording(self):
        """Stop mouse recording by simulating ESC key press"""
        if self.recorder_thread and self.recorder_thread.recorder:
            if self.recorder_thread.recorder.recording:
                try:
                    # Import pynput to simulate ESC key press
                    from pynput.keyboard import Key, Controller
                    
                    # Create keyboard controller and send ESC key
                    keyboard_controller = Controller()
                    keyboard_controller.press(Key.esc)
                    keyboard_controller.release(Key.esc)
                    
                except ImportError:
                    # Fallback to direct thread stop if pynput not available
                    self.recorder_thread.stop_recording()
                except Exception as e:
                    # Fallback to direct thread stop if any error occurs
                    print(f"Error simulating ESC key: {e}")
                    self.recorder_thread.stop_recording()
            
    def on_recording_started(self):
        """Handle recording started"""
        self.start_record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        status_text = "Status: Recording... (Press ESC to stop)"
        self.recording_status.setText(status_text)
        self.recording_timer.setText("00:00:00")
        self.timer_container.show()  # Show the timer container
        self.safe_status_message("Recording in progress...")
        
    def on_recording_stopped(self, filename, event_count):
        """Handle recording stopped"""
        self.start_record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        status_text = f"Status: Recording completed! ({event_count} events)"
        self.recording_status.setText(status_text)
        self.timer_container.hide()  # Hide the timer container
        self.safe_status_message(f"Recording saved: {filename}")
        
        # Update file info
        self.current_recording_file = filename
        self.update_file_info()
        
        # Update replay file input
        self.replay_file_input.setText(filename)
        self.update_replay_file_info(filename)
        
        QMessageBox.information(
            self,
            "Recording Complete",
            f"Recording saved successfully!\n\n"
            f"File: {filename}\n"
            f"Events recorded: {event_count}"
        )
        
    def on_recording_error(self, error_message):
        """Handle recording error"""
        self.start_record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        self.recording_status.setText("Status: Recording error occurred")
        self.timer_container.hide()  # Hide the timer container
        self.safe_status_message("Recording failed")
        
        QMessageBox.critical(
            self, "Recording Error",
            f"Recording failed:\n\n{error_message}"
        )
    
    def on_timer_update(self, time_str):
        """Handle timer update from recording thread"""
        self.recording_timer.setText(time_str)
    
    def on_status_blink(self, show_indicator):
        """Handle blinking recording indicator"""
        if show_indicator:
            self.timer_status.setText("● RECORDING")
            self.timer_status.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #dc3545;
                    background-color: transparent;
                    padding: 5px;
                }
            """)
        else:
            self.timer_status.setText("○ RECORDING")
            self.timer_status.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #6c757d;
                    background-color: transparent;
                    padding: 5px;
                }
            """)
        
    def start_replay(self):
        """Start mouse replay"""
        filename = self.replay_file_input.text().strip()
        if not filename:
            QMessageBox.warning(
                self, "Warning",
                "Please select a recording file to replay."
            )
            return
            
        if not os.path.exists(filename):
            QMessageBox.warning(
                self, "Warning",
                f"Recording file does not exist:\n{filename}"
            )
            return
            
        speed = self.speed_slider.value() / 100.0
        delay = self.delay_spinbox.value()
        
        # Determine replay mode and parameters
        if self.time_mode_radio.isChecked():
            # Time-based replay
            hours = self.replay_hours_spinbox.value()
            minutes = self.replay_minutes_spinbox.value()
            total_hours = hours + (minutes / 60.0)
            
            if total_hours <= 0:
                QMessageBox.warning(
                    self, "Warning",
                    "Please set a valid time duration (hours/minutes)."
                )
                return
                
            replay_times = 1  # Not used in time-based mode
            replay_hours = total_hours
        else:
            # Count-based replay
            replay_times = self.replay_times_spinbox.value()
            replay_hours = 0  # Not used in count-based mode
        
        # Get latency setting
        replay_latency = self.replay_latency_spinbox.value()
        
        # Start replay thread
        self.replay_thread = ReplayThread(filename, speed, delay,
                                          replay_times, replay_hours,
                                          replay_latency)
        self.replay_thread.replay_started.connect(self.on_replay_started)
        self.replay_thread.replay_progress.connect(self.on_replay_progress)
        self.replay_thread.replay_finished.connect(self.on_replay_finished)
        self.replay_thread.replay_error.connect(self.on_replay_error)
        self.replay_thread.replay_count_update.connect(
            self.on_replay_count_update
        )
        
        self.replay_thread.start()
        
    def stop_replay(self):
        """Stop mouse replay"""
        if self.replay_thread and self.replay_thread.isRunning():
            self.replay_thread.terminate()
            self.replay_thread.wait()
            self.on_replay_finished()
            
    def on_replay_started(self):
        """Handle replay started"""
        self.start_replay_button.setEnabled(False)
        self.stop_replay_button.setEnabled(True)
        self.replay_progress_bar.setVisible(True)
        self.replay_progress_bar.setValue(0)
        self.replay_status.setText("Status: Replaying...")
        self.safe_status_message("Replay in progress...")
        
    def on_replay_progress(self, percentage):
        """Handle replay progress update"""
        self.replay_progress_bar.setValue(percentage)
        
    def on_replay_count_update(self, current, total):
        """Handle replay count update"""
        if total == -1:  # Time-based replay
            self.replay_count_status.setText(f"Time-based: Replay #{current}")
        elif total > 1:  # Count-based replay
            self.replay_count_status.setText(f"Replay {current} of {total}")
        else:
            self.replay_count_status.setText("")
        
    def on_replay_finished(self):
        """Handle replay finished"""
        self.start_replay_button.setEnabled(True)
        self.stop_replay_button.setEnabled(False)
        self.replay_progress_bar.setVisible(False)
        self.replay_status.setText("Status: Replay completed!")
        self.replay_count_status.setText("")
        self.safe_status_message("Replay finished")
        
    def on_replay_error(self, error_message):
        """Handle replay error"""
        self.start_replay_button.setEnabled(True)
        self.stop_replay_button.setEnabled(False)
        self.replay_progress_bar.setVisible(False)
        self.replay_status.setText("Status: Replay error occurred")
        self.safe_status_message("Replay failed")
        
        QMessageBox.critical(
            self, "Replay Error", f"Replay failed:\n\n{error_message}"
        )
        
    def closeEvent(self, event):
        """Handle application close"""
        # Stop any running threads
        if self.recorder_thread and self.recorder_thread.isRunning():
            self.recorder_thread.terminate()
            self.recorder_thread.wait()
            
        if self.replay_thread and self.replay_thread.isRunning():
            self.replay_thread.terminate()
            self.replay_thread.wait()
            
        event.accept()


def main():
    """Main function to run the GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Mouse Recorder & Replayer")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MouseRecorderGUI()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
