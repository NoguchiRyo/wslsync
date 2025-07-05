"""
Utility functions for WSL sync tool.

This module provides helper functions for file operations, logging,
and other common tasks.
"""

import logging
import shutil
from pathlib import Path
from typing import List, Optional


def setup_logging(
    log_level: str = "INFO", log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs to console only

    Returns:
        Configured logger instance
    """
    # Convert string level to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "INVALID": logging.INFO,  # Handle invalid levels by defaulting to INFO
    }

    level = level_map.get(log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("wslsync")
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def safe_copy_file(
    source: Path, destination: Path, preserve_timestamps: bool = True
) -> bool:
    """
    Safely copy a file from source to destination with error handling.

    Args:
        source: Source file path
        destination: Destination file path
        preserve_timestamps: Whether to preserve file timestamps

    Returns:
        True if copy was successful, False otherwise

    Raises:
        FileNotFoundError: If source file doesn't exist
        PermissionError: If insufficient permissions
        OSError: If copy operation fails
    """
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    # Create destination directory if needed
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        if preserve_timestamps:
            shutil.copy2(source, destination)
        else:
            shutil.copy(source, destination)
        return True
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied copying {source} to {destination}"
        ) from e
    except OSError as e:
        raise OSError(f"Failed to copy {source} to {destination}") from e


def safe_remove_file(file_path: Path) -> bool:
    """
    Safely remove a file with error handling.

    Args:
        file_path: Path to file to remove

    Returns:
        True if removal was successful, False otherwise

    Raises:
        PermissionError: If insufficient permissions
        OSError: If removal fails
    """
    if not file_path.exists():
        return False

    if file_path.is_dir():
        raise OSError(f"Cannot remove directory with safe_remove_file: {file_path}")

    try:
        file_path.unlink()
        return True
    except PermissionError as e:
        raise PermissionError(f"Permission denied removing {file_path}") from e
    except OSError as e:
        raise OSError(f"Failed to remove {file_path}") from e


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist
        OSError: If stat operation fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.is_dir():
        raise OSError(f"Cannot get size of directory: {file_path}")

    try:
        return file_path.stat().st_size
    except OSError as e:
        raise OSError(f"Failed to get size of {file_path}") from e


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    """
    Get relative path of a file from a base directory.

    Args:
        file_path: Full path to file
        base_path: Base directory path

    Returns:
        Relative path from base to file

    Raises:
        ValueError: If file_path is not under base_path
    """
    try:
        return file_path.relative_to(base_path)
    except ValueError as e:
        raise ValueError(f"Path {file_path} is not under base path {base_path}") from e


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path to create

    Raises:
        PermissionError: If insufficient permissions to create directory
        OSError: If directory creation fails
    """
    if directory.exists() and not directory.is_dir():
        raise OSError(f"Path exists but is not a directory: {directory}")

    try:
        directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied creating directory: {directory}"
        ) from e
    except OSError as e:
        raise OSError(f"Failed to create directory: {directory}") from e


def is_path_safe(path: Path, base_path: Path) -> bool:
    """
    Check if a path is safe (doesn't escape base directory).

    Args:
        path: Path to check
        base_path: Base directory that should contain the path

    Returns:
        True if path is safe (within base_path), False otherwise
    """
    try:
        # Handle relative paths by treating them as safe if they are under base
        if not path.is_absolute():
            # For relative paths, join with base and check if it stays under base
            full_path = (base_path / path).resolve()
            resolved_base = base_path.resolve()
            full_path.relative_to(resolved_base)
            return True
        else:
            # Resolve both paths to absolute paths
            resolved_path = path.resolve()
            resolved_base = base_path.resolve()

            # Check if the resolved path is under the base path
            resolved_path.relative_to(resolved_base)
            return True
    except ValueError:
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB", "256 KB")
    """
    if size_bytes < 0:
        return "0 B"

    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def get_sync_summary(copied_files: List[Path], deleted_files: List[Path]) -> str:
    """
    Generate a summary of sync operations.

    Args:
        copied_files: List of files that were copied
        deleted_files: List of files that were deleted

    Returns:
        Formatted summary string
    """
    copied_count = len(copied_files)
    deleted_count = len(deleted_files)

    summary = (
        f"Sync completed: {copied_count} files copied, {deleted_count} files deleted"
    )

    if copied_count > 0:
        summary += f"\nCopied files:"
        for file_path in copied_files:
            summary += f"\n  - {file_path.name}"

    if deleted_count > 0:
        summary += f"\nDeleted files:"
        for file_path in deleted_files:
            summary += f"\n  - {file_path.name}"

    return summary
