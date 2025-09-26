#!/usr/bin/env python3
"""
Mouse Recorder GUI Application using PyQt6
Provides an easy-to-use interface for recording and replaying mouse actions
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, QSlider,
    QSpinBox, QFileDialog, QMessageBox, QProgressBar, QComboBox,
    QCheckBox, QFrame, QSplitter, QTabWidget
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src" / "test"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from mouse_recorder import MouseRecorder
from mouse_replayer import MouseReplayer


class RecorderThread(QThread):
    """Thread for handling mouse recording"""
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str, int)  # filename, event_count
    recording_error = pyqtSignal(str)
    
    def __init__(self, output_file):
        super().__init__()
        self.output_file = output_file
        self.recorder = None
        
    def run(self):
        try:
            self.recorder = MouseRecorder(self.output_file)
            self.recording_started.emit()
            self.recorder.start_recording()
            # Recording stops when ESC is pressed
            event_count = len(self.recorder.events) if self.recorder.events else 0
            self.recording_stopped.emit(self.output_file, event_count)
        except Exception as e:
            self.recording_error.emit(str(e))
    
    def stop_recording(self):
        if self.recorder and self.recorder.recording:
            self.recorder.stop_recording()


class ReplayThread(QThread):
    """Thread for handling mouse replay"""
    replay_started = pyqtSignal()
    replay_progress = pyqtSignal(int)  # percentage
    replay_finished = pyqtSignal()
    replay_error = pyqtSignal(str)
    
    def __init__(self, recording_file, speed=1.0, delay_start=3):
        super().__init__()
        self.recording_file = recording_file
        self.speed = speed
        self.delay_start = delay_start
        self.replayer = None
        
    def run(self):
        try:
            self.replayer = MouseReplayer(self.recording_file)
            if not self.replayer.load_recording():
                self.replay_error.emit("Failed to load recording file")
                return
                
            self.replay_started.emit()
            
            # Custom replay with progress updates
            events = self.replayer.recording_data['events']
            if not events:
                self.replay_error.emit("No events to replay")
                return
                
            # Countdown delay
            for i in range(self.delay_start, 0, -1):
                time.sleep(1)
                
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
                
                # Update progress
                progress = int((i / len(events)) * 100)
                self.replay_progress.emit(progress)
                
            self.replay_finished.emit()
            
        except Exception as e:
            self.replay_error.emit(str(e))


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
        self.statusBar().showMessage("Ready")
        
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
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_record_button)
        button_layout.addWidget(self.stop_record_button)
        
        controls_layout.addLayout(button_layout)
        controls_layout.addWidget(self.recording_status)
        
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
        
        ⚠️ Note: The recording captures all mouse movements, clicks, and scrolls
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
        self.replay_file_input.setPlaceholderText("Enter recording file to replay...")
        
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
        
        settings_layout.addLayout(speed_layout)
        settings_layout.addLayout(delay_layout)
        
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
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_replay_button)
        button_layout.addWidget(self.stop_replay_button)
        
        controls_layout.addLayout(button_layout)
        controls_layout.addWidget(self.replay_progress_bar)
        controls_layout.addWidget(self.replay_status)
        
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
        <p><b>Description:</b> A GUI application for recording and replaying mouse actions</p>
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
            self.recording_info.setPlainText(f"File does not exist: {filename}")
            
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
            QMessageBox.warning(self, "Warning", "Please enter a filename for the recording.")
            return
            
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Start recording thread
        self.recorder_thread = RecorderThread(filename)
        self.recorder_thread.recording_started.connect(self.on_recording_started)
        self.recorder_thread.recording_stopped.connect(self.on_recording_stopped)
        self.recorder_thread.recording_error.connect(self.on_recording_error)
        
        self.recorder_thread.start()
        
    def stop_recording(self):
        """Stop mouse recording"""
        if self.recorder_thread:
            self.recorder_thread.stop_recording()
            
    def on_recording_started(self):
        """Handle recording started"""
        self.start_record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        self.recording_status.setText("Status: Recording... (Press ESC to stop)")
        self.statusBar().showMessage("Recording in progress...")
        
    def on_recording_stopped(self, filename, event_count):
        """Handle recording stopped"""
        self.start_record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        self.recording_status.setText(f"Status: Recording completed! ({event_count} events)")
        self.statusBar().showMessage(f"Recording saved: {filename}")
        
        # Update file info
        self.current_recording_file = filename
        self.update_file_info()
        
        # Update replay file input
        self.replay_file_input.setText(filename)
        self.update_replay_file_info(filename)
        
        QMessageBox.information(
            self,
            "Recording Complete",
            f"Recording saved successfully!\n\nFile: {filename}\nEvents recorded: {event_count}"
        )
        
    def on_recording_error(self, error_message):
        """Handle recording error"""
        self.start_record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        self.recording_status.setText("Status: Recording error occurred")
        self.statusBar().showMessage("Recording failed")
        
        QMessageBox.critical(self, "Recording Error", f"Recording failed:\n\n{error_message}")
        
    def start_replay(self):
        """Start mouse replay"""
        filename = self.replay_file_input.text().strip()
        if not filename:
            QMessageBox.warning(self, "Warning", "Please select a recording file to replay.")
            return
            
        if not os.path.exists(filename):
            QMessageBox.warning(self, "Warning", f"Recording file does not exist:\n{filename}")
            return
            
        speed = self.speed_slider.value() / 100.0
        delay = self.delay_spinbox.value()
        
        # Start replay thread
        self.replay_thread = ReplayThread(filename, speed, delay)
        self.replay_thread.replay_started.connect(self.on_replay_started)
        self.replay_thread.replay_progress.connect(self.on_replay_progress)
        self.replay_thread.replay_finished.connect(self.on_replay_finished)
        self.replay_thread.replay_error.connect(self.on_replay_error)
        
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
        self.statusBar().showMessage("Replay in progress...")
        
    def on_replay_progress(self, percentage):
        """Handle replay progress update"""
        self.replay_progress_bar.setValue(percentage)
        
    def on_replay_finished(self):
        """Handle replay finished"""
        self.start_replay_button.setEnabled(True)
        self.stop_replay_button.setEnabled(False)
        self.replay_progress_bar.setVisible(False)
        self.replay_status.setText("Status: Replay completed!")
        self.statusBar().showMessage("Replay finished")
        
    def on_replay_error(self, error_message):
        """Handle replay error"""
        self.start_replay_button.setEnabled(True)
        self.stop_replay_button.setEnabled(False)
        self.replay_progress_bar.setVisible(False)
        self.replay_status.setText("Status: Replay error occurred")
        self.statusBar().showMessage("Replay failed")
        
        QMessageBox.critical(self, "Replay Error", f"Replay failed:\n\n{error_message}")
        
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