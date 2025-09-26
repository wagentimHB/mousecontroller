"""
Module utilities for mouse controller package.

Provides utilities for dynamic module imports and module management.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Any, Union


def import_module_from_path(module_name: str, file_path: Union[str, Path]) -> Any:
    """
    Import a module from a specific file path.
    
    Args:
        module_name: Name to give the imported module
        file_path: Path to the Python file to import
        
    Returns:
        Imported module object
        
    Raises:
        ImportError: If the module cannot be loaded
    """
    file_path = Path(file_path)
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot load module {module_name} from {file_path}"
        )
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup_project_path(reference_file: Union[str, Path] = None) -> None:
    """
    Set up project paths for imports (simplified version).
    
    Args:
        reference_file: Reference file to determine project structure
    """
    from .path_utils import setup_project_paths
    setup_project_paths(reference_file)


def get_mousecontroller_modules(base_path: Path = None):
    """
    Get MouseRecorder and MouseReplayer classes from their modules.
    
    Args:
        base_path: Base path where the modules are located
        
    Returns:
        Tuple of (MouseRecorder, MouseReplayer) classes
        
    Raises:
        ImportError: If modules cannot be imported
    """
    if base_path is None:
        from .path_utils import get_mousecontroller_path
        base_path = get_mousecontroller_path()
    
    try:
        # Import MouseRecorder
        recorder_module = import_module_from_path(
            "mouse_recorder", base_path / "mouse_recorder.py"
        )
        
        # Import MouseReplayer  
        replayer_module = import_module_from_path(
            "mouse_replayer", base_path / "mouse_replayer.py"
        )
        
        return recorder_module.MouseRecorder, replayer_module.MouseReplayer
        
    except ImportError as e:
        raise ImportError(
            f"Error importing MouseRecorder/MouseReplayer modules: {e}"
        ) from e


def import_gui_module(base_path: Path = None):
    """
    Import the GUI module dynamically.
    
    Args:
        base_path: Base path where the GUI module is located
        
    Returns:
        GUI module object
        
    Raises:
        ImportError: If GUI module cannot be imported
    """
    if base_path is None:
        from .path_utils import get_mousecontroller_path
        base_path = get_mousecontroller_path()
    
    return import_module_from_path(
        "mouse_recorder_gui", base_path / "mouse_recorder_gui.py"
    )