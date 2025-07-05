"""
Core synchronization functionality for WSL sync tool.

This module handles the main file synchronization operations between
Windows and WSL2 file systems.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set

from .config import WSLSyncConfig


class WSLSyncEngine:
    """Main synchronization engine."""

    def __init__(self, config: WSLSyncConfig) -> None:
        """
        Initialize sync engine with configuration.

        Args:
            config: Configuration object containing sync settings
        """
        if config is None:
            raise ValueError("Config cannot be None")
        self.config = config

    def sync(self) -> None:
        """
        Execute complete synchronization workflow.

        This performs the full sync process:
        1. Validate source and destination paths
        2. Copy files from source to destination
        3. Clean up unwanted files in destination

        Raises:
            FileNotFoundError: If source files or directories don't exist
            PermissionError: If insufficient permissions for file operations
            OSError: If file system operations fail
        """
        # Step 1: Validate paths
        self.validate_paths()

        # Step 2: Copy files
        copied_files = self.copy_files()

        # Step 3: Cleanup destination
        keep_files = set(copied_files)
        self.cleanup_destination(keep_files)

    def copy_files(self) -> List[Path]:
        """
        Copy files and directories from Windows source to WSL2 destination.

        Returns:
            List of successfully copied file paths

        Raises:
            FileNotFoundError: If source files/directories don't exist
            PermissionError: If insufficient permissions
            OSError: If copy operations fail
        """
        if not self.config.windows_base or not self.config.wsl2_base:
            raise ValueError("Source and destination paths must be configured")

        copied_files: List[Path] = []

        for file_rel_path in self.config.files:
            source_path = self.config.windows_base / file_rel_path
            dest_path = self.config.wsl2_base / file_rel_path

            if not source_path.exists():
                raise FileNotFoundError(f"Source path not found: {source_path}")

            if source_path.is_file():
                # Handle single file
                self.create_directory_structure(dest_path)
                try:
                    shutil.copy2(source_path, dest_path)
                    copied_files.append(dest_path)
                except PermissionError as e:
                    raise PermissionError(
                        f"Permission denied copying {source_path} to {dest_path}"
                    ) from e
                except OSError as e:
                    raise OSError(f"Failed to copy {source_path} to {dest_path}") from e

            elif source_path.is_dir():
                # Handle directory recursively
                try:
                    # Remove destination directory if it exists to ensure clean copy
                    if dest_path.exists():
                        shutil.rmtree(dest_path)

                    # Copy entire directory tree
                    shutil.copytree(source_path, dest_path)

                    # Set secure permissions (755) for all copied directories
                    os.chmod(dest_path, 0o755)  # Root directory first
                    for copied_dir in dest_path.rglob("*"):
                        if copied_dir.is_dir():
                            os.chmod(copied_dir, 0o755)

                    # Add all copied files to the list
                    for copied_file in dest_path.rglob("*"):
                        if copied_file.is_file():
                            copied_files.append(copied_file)

                except PermissionError as e:
                    raise PermissionError(
                        f"Permission denied copying directory {source_path} to {dest_path}"
                    ) from e
                except OSError as e:
                    raise OSError(
                        f"Failed to copy directory {source_path} to {dest_path}"
                    ) from e

        return copied_files

    def cleanup_destination(self, keep_files: Set[Path]) -> List[Path]:
        """
        Remove files from destination that are not in the sync list.

        Args:
            keep_files: Set of file paths that should be preserved

        Returns:
            List of deleted file paths

        Raises:
            PermissionError: If insufficient permissions for deletion
            OSError: If deletion operations fail
        """
        if not self.config.wsl2_base:
            raise ValueError("Destination path must be configured")

        deleted_files: List[Path] = []

        # Get all files in destination
        all_dest_files = self.get_destination_files()

        # Delete files not in keep_files or under configured directories
        for file_path in all_dest_files:
            should_keep = file_path in keep_files

            # Check if file is under any configured directory
            if not should_keep:
                rel_path = file_path.relative_to(self.config.wsl2_base)
                for config_path in self.config.files:
                    if str(rel_path) == config_path or str(rel_path).startswith(
                        config_path + "/"
                    ):
                        should_keep = True
                        break

            if not should_keep:
                try:
                    file_path.unlink()
                    deleted_files.append(file_path)
                except PermissionError as e:
                    raise PermissionError(
                        f"Permission denied deleting {file_path}"
                    ) from e
                except OSError as e:
                    raise OSError(f"Failed to delete {file_path}") from e

        # Remove empty directories
        for item in list(self.config.wsl2_base.rglob("*")):
            if item.is_dir() and not any(item.iterdir()):
                try:
                    item.rmdir()
                except (PermissionError, OSError):
                    # Ignore errors removing empty directories
                    pass

        return deleted_files

    def validate_paths(self) -> bool:
        """
        Validate that source and destination paths exist and are accessible.

        Returns:
            True if all paths are valid and accessible

        Raises:
            FileNotFoundError: If required paths don't exist
            PermissionError: If paths are not accessible
        """
        if not self.config.windows_base:
            raise ValueError("Windows base path not configured")

        if not self.config.wsl2_base:
            raise ValueError("WSL2 base path not configured")

        if not self.config.windows_base.exists():
            raise FileNotFoundError(
                f"Source directory not found: {self.config.windows_base}"
            )

        if not self.config.wsl2_base.exists():
            raise FileNotFoundError(
                f"Destination directory not found: {self.config.wsl2_base}"
            )

        # Check if paths are accessible
        try:
            list(self.config.windows_base.iterdir())
        except PermissionError as e:
            raise PermissionError(
                f"Cannot access source directory: {self.config.windows_base}"
            ) from e

        try:
            list(self.config.wsl2_base.iterdir())
        except PermissionError as e:
            raise PermissionError(
                f"Cannot access destination directory: {self.config.wsl2_base}"
            ) from e

        return True

    def get_source_files(self) -> List[Path]:
        """
        Get list of all source files to be synchronized (including files in directories).

        Returns:
            List of source file paths that exist and are readable

        Raises:
            FileNotFoundError: If source directory doesn't exist
        """
        if not self.config.windows_base:
            raise ValueError("Windows base path not configured")

        if not self.config.windows_base.exists():
            raise FileNotFoundError(
                f"Source directory not found: {self.config.windows_base}"
            )

        source_files: List[Path] = []

        for file_rel_path in self.config.files:
            source_path = self.config.windows_base / file_rel_path
            if source_path.exists():
                if source_path.is_file():
                    source_files.append(source_path)
                elif source_path.is_dir():
                    # Add all files in the directory recursively
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            source_files.append(file_path)

        return source_files

    def get_destination_files(self) -> List[Path]:
        """
        Get list of all files currently in destination directory.

        Returns:
            List of all files in destination directory

        Raises:
            FileNotFoundError: If destination directory doesn't exist
        """
        if not self.config.wsl2_base:
            raise ValueError("WSL2 base path not configured")

        if not self.config.wsl2_base.exists():
            raise FileNotFoundError(
                f"Destination directory not found: {self.config.wsl2_base}"
            )

        dest_files: List[Path] = []

        for item in self.config.wsl2_base.rglob("*"):
            if item.is_file():
                dest_files.append(item)

        return dest_files

    def create_directory_structure(self, file_path: Path) -> None:
        """
        Create necessary directory structure for a file path with secure permissions.

        Args:
            file_path: Path to file, directories will be created for parent dirs

        Raises:
            PermissionError: If insufficient permissions to create directories
            OSError: If directory creation fails
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # Set secure permissions (755) for newly created directories under wsl2_base
            if self.config.wsl2_base:
                for parent in file_path.parents:
                    if (parent.exists() and 
                        parent != self.config.wsl2_base and 
                        self.config.wsl2_base in parent.parents):
                        try:
                            os.chmod(parent, 0o755)
                        except (PermissionError, OSError):
                            # Skip if we can't set permissions (e.g., system directories)
                            pass
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied creating directory: {file_path.parent}"
            ) from e
        except OSError as e:
            raise OSError(f"Failed to create directory: {file_path.parent}") from e
