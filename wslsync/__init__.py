"""
WSL Sync Tool - Synchronize files between Windows and WSL2 systems.

A command-line tool that reads a .wslsync configuration file and synchronizes
specified files from Windows to WSL2, cleaning up unwanted files in the destination.
"""

__version__ = "0.1.0"
__author__ = "WSL Sync Tool"
__email__ = "noreply@example.com"

from .config import WSLSyncConfig, parse_config, validate_config, get_default_config_path
from .sync import WSLSyncEngine
from .utils import setup_logging

__all__ = [
    "WSLSyncConfig",
    "parse_config", 
    "validate_config",
    "get_default_config_path",
    "WSLSyncEngine",
    "setup_logging",
]