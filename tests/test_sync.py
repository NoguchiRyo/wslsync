#!/usr/bin/env python3
"""
TDD tests for sync.py module
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from wslsync.config import WSLSyncConfig
from wslsync.sync import WSLSyncEngine


class TestWSLSyncEngine(unittest.TestCase):
    """Test cases for WSLSyncEngine class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = WSLSyncConfig(
            windows_base=Path("/mnt/c/source"),
            wsl2_base=Path("/home/user/dest"),
            files=["file1.txt", "subdir/file2.txt", "file3.txt"],
        )

        # Create temporary directories for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.temp_dir / "source"
        self.dest_dir = self.temp_dir / "dest"
        self.source_dir.mkdir()
        self.dest_dir.mkdir()

        # Create test files in source
        (self.source_dir / "file1.txt").write_text("content1")
        (self.source_dir / "subdir").mkdir()
        (self.source_dir / "subdir" / "file2.txt").write_text("content2")
        (self.source_dir / "file3.txt").write_text("content3")

        # Create some files in dest that should be cleaned up
        (self.dest_dir / "old_file.txt").write_text("old content")
        (self.dest_dir / "temp.log").write_text("temp data")

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_wslsync_engine_initialization(self):
        """Test WSLSyncEngine initialization"""
        # This will fail until WSLSyncEngine.__init__ is implemented
        engine = WSLSyncEngine(self.test_config)

        self.assertIsNotNone(engine)
        self.assertEqual(engine.config, self.test_config)

    def test_wslsync_engine_initialization_with_none_config(self):
        """Test WSLSyncEngine initialization with None config"""
        with self.assertRaises(ValueError):
            WSLSyncEngine(None)

    def test_sync_complete_workflow(self):
        """Test complete sync workflow"""
        engine = WSLSyncEngine(self.test_config)

        # Mock the config to use our test directories
        engine.config.windows_base = self.source_dir
        engine.config.wsl2_base = self.dest_dir

        # This will fail until sync() is implemented
        result = engine.sync()

        # Verify sync completed successfully
        self.assertIsNone(result)  # sync() returns None on success

        # Verify files were copied
        self.assertTrue((self.dest_dir / "file1.txt").exists())
        self.assertTrue((self.dest_dir / "subdir" / "file2.txt").exists())
        self.assertTrue((self.dest_dir / "file3.txt").exists())

        # Verify old files were cleaned up
        self.assertFalse((self.dest_dir / "old_file.txt").exists())
        self.assertFalse((self.dest_dir / "temp.log").exists())

    def test_sync_with_nonexistent_source(self):
        """Test sync with non-existent source directory"""
        config = WSLSyncConfig(
            windows_base=Path("/nonexistent/source"),
            wsl2_base=self.dest_dir,
            files=["file1.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.sync()

    def test_sync_with_nonexistent_dest(self):
        """Test sync with non-existent destination directory"""
        config = WSLSyncConfig(
            windows_base=self.source_dir,
            wsl2_base=Path("/nonexistent/dest"),
            files=["file1.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.sync()

    def test_copy_files_success(self):
        """Test successful file copying"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.windows_base = self.source_dir
        engine.config.wsl2_base = self.dest_dir

        # This will fail until copy_files() is implemented
        copied_files = engine.copy_files()

        self.assertIsInstance(copied_files, list)
        self.assertEqual(len(copied_files), 3)

        # Verify files were actually copied
        for file_path in ["file1.txt", "subdir/file2.txt", "file3.txt"]:
            dest_file = self.dest_dir / file_path
            self.assertTrue(dest_file.exists())
            self.assertIn(dest_file, copied_files)

    def test_copy_files_missing_source_file(self):
        """Test copying when source file is missing"""
        config = WSLSyncConfig(
            windows_base=self.source_dir,
            wsl2_base=self.dest_dir,
            files=["missing_file.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.copy_files()

    def test_copy_files_permission_error(self):
        """Test copying with permission errors"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.windows_base = self.source_dir
        engine.config.wsl2_base = Path("/root/restricted")  # Restricted path

        # This should raise PermissionError
        with self.assertRaises(PermissionError):
            engine.copy_files()

    def test_cleanup_destination_success(self):
        """Test successful cleanup of destination"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.wsl2_base = self.dest_dir

        # Files to keep
        keep_files = {
            self.dest_dir / "file1.txt",
            self.dest_dir / "subdir" / "file2.txt",
        }

        # Create the files to keep
        for file_path in keep_files:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("keep this")

        # This will fail until cleanup_destination() is implemented
        deleted_files = engine.cleanup_destination(keep_files)

        self.assertIsInstance(deleted_files, list)
        self.assertEqual(len(deleted_files), 2)  # old_file.txt and temp.log

        # Verify old files were deleted
        self.assertFalse((self.dest_dir / "old_file.txt").exists())
        self.assertFalse((self.dest_dir / "temp.log").exists())

        # Verify keep files still exist
        for file_path in keep_files:
            self.assertTrue(file_path.exists())

    def test_cleanup_destination_empty_keep_set(self):
        """Test cleanup with empty keep set (should delete everything)"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.wsl2_base = self.dest_dir

        deleted_files = engine.cleanup_destination(set())

        self.assertIsInstance(deleted_files, list)
        self.assertEqual(len(deleted_files), 2)  # All files deleted

        # Verify all files were deleted
        self.assertFalse((self.dest_dir / "old_file.txt").exists())
        self.assertFalse((self.dest_dir / "temp.log").exists())

    def test_validate_paths_success(self):
        """Test successful path validation"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.windows_base = self.source_dir
        engine.config.wsl2_base = self.dest_dir

        # This will fail until validate_paths() is implemented
        result = engine.validate_paths()

        self.assertTrue(result)

    def test_validate_paths_missing_source(self):
        """Test path validation with missing source"""
        config = WSLSyncConfig(
            windows_base=Path("/nonexistent/source"),
            wsl2_base=self.dest_dir,
            files=["file1.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.validate_paths()

    def test_validate_paths_missing_dest(self):
        """Test path validation with missing destination"""
        config = WSLSyncConfig(
            windows_base=self.source_dir,
            wsl2_base=Path("/nonexistent/dest"),
            files=["file1.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.validate_paths()

    def test_get_source_files_success(self):
        """Test getting source files successfully"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.windows_base = self.source_dir

        # This will fail until get_source_files() is implemented
        source_files = engine.get_source_files()

        self.assertIsInstance(source_files, list)
        self.assertEqual(len(source_files), 3)

        expected_files = [
            self.source_dir / "file1.txt",
            self.source_dir / "subdir" / "file2.txt",
            self.source_dir / "file3.txt",
        ]

        for expected_file in expected_files:
            self.assertIn(expected_file, source_files)

    def test_get_source_files_missing_directory(self):
        """Test getting source files with missing directory"""
        config = WSLSyncConfig(
            windows_base=Path("/nonexistent/source"),
            wsl2_base=self.dest_dir,
            files=["file1.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.get_source_files()

    def test_get_destination_files_success(self):
        """Test getting destination files successfully"""
        engine = WSLSyncEngine(self.test_config)
        engine.config.wsl2_base = self.dest_dir

        # This will fail until get_destination_files() is implemented
        dest_files = engine.get_destination_files()

        self.assertIsInstance(dest_files, list)
        self.assertEqual(len(dest_files), 2)  # old_file.txt and temp.log

        expected_files = [self.dest_dir / "old_file.txt", self.dest_dir / "temp.log"]

        for expected_file in expected_files:
            self.assertIn(expected_file, dest_files)

    def test_get_destination_files_empty_directory(self):
        """Test getting destination files from empty directory"""
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()

        engine = WSLSyncEngine(self.test_config)
        engine.config.wsl2_base = empty_dir

        dest_files = engine.get_destination_files()

        self.assertIsInstance(dest_files, list)
        self.assertEqual(len(dest_files), 0)

    def test_get_destination_files_missing_directory(self):
        """Test getting destination files with missing directory"""
        config = WSLSyncConfig(
            windows_base=self.source_dir,
            wsl2_base=Path("/nonexistent/dest"),
            files=["file1.txt"],
        )
        engine = WSLSyncEngine(config)

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            engine.get_destination_files()

    def test_create_directory_structure_success(self):
        """Test creating directory structure successfully"""
        engine = WSLSyncEngine(self.test_config)

        test_file_path = self.dest_dir / "deep" / "nested" / "dirs" / "file.txt"

        # This will fail until create_directory_structure() is implemented
        engine.create_directory_structure(test_file_path)

        # Verify directories were created
        self.assertTrue(test_file_path.parent.exists())
        self.assertTrue(test_file_path.parent.is_dir())

    def test_create_directory_structure_existing_dirs(self):
        """Test creating directory structure when directories already exist"""
        engine = WSLSyncEngine(self.test_config)

        # Create some directories first
        existing_dir = self.dest_dir / "existing" / "dir"
        existing_dir.mkdir(parents=True)

        test_file_path = existing_dir / "subdir" / "file.txt"

        # This should not raise an error
        engine.create_directory_structure(test_file_path)

        # Verify directories exist
        self.assertTrue(test_file_path.parent.exists())
        self.assertTrue(test_file_path.parent.is_dir())

    def test_create_directory_structure_permission_error(self):
        """Test creating directory structure with permission errors"""
        engine = WSLSyncEngine(self.test_config)

        # Try to create directory in restricted location
        restricted_path = Path("/root/restricted/dir/file.txt")

        # This should raise PermissionError
        with self.assertRaises(PermissionError):
            engine.create_directory_structure(restricted_path)


if __name__ == "__main__":
    unittest.main()
