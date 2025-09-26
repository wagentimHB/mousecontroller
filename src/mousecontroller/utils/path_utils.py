"""
Path utilities for mouse controller package.

Provides utilities for path management and project structure navigation.
"""

import sys
from pathlib import Path
from typing import Union


def get_project_root(start_path: Union[str, Path] = None) -> Path:
    """
    Get the project root directory.
    
    Args:
        start_path: Starting path to search from (defaults to current file's parent)
        
    Returns:
        Path to project root directory
    """
    if start_path is None:
        # Find project root by looking for markers like pyproject.toml, .git, etc.
        current = Path(__file__).parent
        while current != current.parent:
            if any((current / marker).exists() for marker in 
                   ['pyproject.toml', '.git', 'requirements.txt']):
                return current
            current = current.parent
        return Path(__file__).parent.parent.parent.parent
    
    return Path(start_path)


def get_src_path(project_root: Path = None) -> Path:
    """
    Get the src directory path.
    
    Args:
        project_root: Project root directory (auto-detected if not provided)
        
    Returns:
        Path to src directory
    """
    if project_root is None:
        project_root = get_project_root()
    
    return project_root / "src"


def get_mousecontroller_path(project_root: Path = None) -> Path:
    """
    Get the mousecontroller package path.
    
    Args:
        project_root: Project root directory (auto-detected if not provided)
        
    Returns:
        Path to mousecontroller package
    """
    return get_src_path(project_root) / "mousecontroller"


def ensure_path_in_sys(path: Union[str, Path]) -> bool:
    """
    Ensure a path is in sys.path for imports.
    
    Args:
        path: Path to add to sys.path
        
    Returns:
        True if path was added, False if already present
    """
    str_path = str(Path(path).resolve())
    
    if str_path not in sys.path:
        sys.path.insert(0, str_path)
        return True
    
    return False


def setup_project_paths(reference_file: Union[str, Path] = None) -> dict:
    """
    Set up all project paths and add necessary paths to sys.path.
    
    Args:
        reference_file: Reference file to determine project structure
        
    Returns:
        Dictionary with all relevant paths
    """
    if reference_file is None:
        project_root = get_project_root()
    else:
        # Navigate up from reference file to find project root
        ref_path = Path(reference_file).parent
        project_root = get_project_root(ref_path)
    
    paths = {
        'project_root': project_root,
        'src': get_src_path(project_root),
        'mousecontroller': get_mousecontroller_path(project_root),
        'data': project_root / 'data',
        'tests': project_root / 'tests',
        'docs': project_root / 'docs'
    }
    
    # Add necessary paths to sys.path
    ensure_path_in_sys(paths['src'])
    ensure_path_in_sys(paths['mousecontroller'])
    
    return paths