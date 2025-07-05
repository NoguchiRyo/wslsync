"""
Configuration parser for WSL sync tool.

This module handles parsing and validation of .wslsync configuration files.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class WSLSyncConfig:
    """Configuration data structure for WSL sync operations."""

    windows_base: Optional[Path] = None
    wsl2_base: Optional[Path] = None
    files: List[str] = field(default_factory=list)


def parse_config(config_path: Path) -> WSLSyncConfig:
    """
    Parse .wslsync configuration file.

    Args:
        config_path: Path to the .wslsync configuration file

    Returns:
        WSLSyncConfig object containing parsed configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    content = config_path.read_text().strip()
    if not content:
        raise ValueError("Config file is empty")

    config = WSLSyncConfig()

    # Remove comments and empty lines
    lines = []
    for line in content.split("\n"):
        line = line.split("#")[0].strip()  # Remove comments
        if line:
            lines.append(line)

    content_clean = "\n".join(lines)

    # Parse windows_base
    windows_match = re.search(r"windows_base\s*=\s*(.+)", content_clean)
    if not windows_match:
        raise ValueError("Missing required field: windows_base")
    config.windows_base = Path(windows_match.group(1).strip())

    # Parse wsl2_base
    wsl2_match = re.search(r"wsl2_base\s*=\s*(.+)", content_clean)
    if not wsl2_match:
        raise ValueError("Missing required field: wsl2_base")
    config.wsl2_base = Path(wsl2_match.group(1).strip())

    # Parse files list
    files_match = re.search(r"files\s*=\s*\[(.*?)\]", content_clean, re.DOTALL)
    if not files_match:
        raise ValueError("Missing required field: files")

    files_str = files_match.group(1).strip()
    if files_str:
        # Parse comma-separated quoted strings
        file_entries = re.findall(r'"([^"]*)"', files_str)
        config.files = file_entries

    return config


def validate_config(config: WSLSyncConfig) -> bool:
    """
    Validate configuration settings.

    Args:
        config: Configuration object to validate

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid with details
    """
    if config.windows_base is None:
        raise ValueError("windows_base is required")

    if config.wsl2_base is None:
        raise ValueError("wsl2_base is required")

    if not config.files:
        raise ValueError("files list cannot be empty")

    # Check for empty paths
    if str(config.windows_base).strip() == "" or str(config.windows_base) == ".":
        raise ValueError("Invalid path format: windows_base path cannot be empty")

    if str(config.wsl2_base).strip() == "" or str(config.wsl2_base) == ".":
        raise ValueError("Invalid path format: wsl2_base path cannot be empty")

    # Check for duplicate files
    if len(config.files) != len(set(config.files)):
        raise ValueError("Duplicate files found in configuration")

    return True


def get_default_config_path() -> Path:
    """
    Get the default path for .wslsync config file.

    Returns:
        Path to default config file location (home directory)
    """
    return Path.home() / ".wslsync"
