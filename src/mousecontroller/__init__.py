"""
Mouse Recorder and Replayer Package

This package provides functionality to record and replay mouse movements,
clicks, and scroll actions.
"""

from .mouse_recorder import MouseRecorder
from .mouse_replayer import MouseReplayer

__version__ = "1.0.0"
__all__ = ["MouseRecorder", "MouseReplayer"]