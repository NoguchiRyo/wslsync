#!/usr/bin/env python3
"""
TDD tests for utils.py module
"""

import unittest
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from wslsync.utils import (
    setup_logging, safe_copy_file, safe_remove_file, get_file_size,
    get_relative_path, ensure_directory_exists, is_path_safe,
    format_file_size, get_sync_summary
)


class TestSetupLogging(unittest.TestCase):
    """Test cases for setup_logging function"""
    
    def test_setup_logging_default_config(self):
        """Test setup_logging with default configuration"""
        # This will fail until setup_logging is implemented
        logger = setup_logging()
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.INFO)
    
    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom log level"""
        logger = setup_logging(log_level="DEBUG")
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.DEBUG)
    
    def test_setup_logging_with_file(self):
        """Test setup_logging with log file"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            log_file = Path(f.name)
        
        logger = setup_logging(log_level="WARNING", log_file=log_file)
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.WARNING)
        
        # Clean up
        log_file.unlink()
    
    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level"""
        # This should handle invalid log levels gracefully
        logger = setup_logging(log_level="INVALID")
        
        self.assertIsInstance(logger, logging.Logger)
        # Should default to INFO level
        self.assertEqual(logger.level, logging.INFO)


class TestSafeCopyFile(unittest.TestCase):
    """Test cases for safe_copy_file function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.source_file = self.temp_dir / "source.txt"
        self.dest_file = self.temp_dir / "dest.txt"
        
        # Create source file
        self.source_file.write_text("test content")
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_safe_copy_file_success(self):
        """Test successful file copy"""
        # This will fail until safe_copy_file is implemented
        result = safe_copy_file(self.source_file, self.dest_file)
        
        self.assertTrue(result)
        self.assertTrue(self.dest_file.exists())
        self.assertEqual(self.source_file.read_text(), self.dest_file.read_text())
    
    def test_safe_copy_file_preserve_timestamps(self):
        """Test file copy with timestamp preservation"""
        result = safe_copy_file(self.source_file, self.dest_file, preserve_timestamps=True)
        
        self.assertTrue(result)
        self.assertTrue(self.dest_file.exists())
        
        # Verify timestamps are preserved (within 1 second tolerance)
        source_mtime = self.source_file.stat().st_mtime
        dest_mtime = self.dest_file.stat().st_mtime
        self.assertAlmostEqual(source_mtime, dest_mtime, delta=1.0)
    
    def test_safe_copy_file_no_preserve_timestamps(self):
        """Test file copy without timestamp preservation"""
        result = safe_copy_file(self.source_file, self.dest_file, preserve_timestamps=False)
        
        self.assertTrue(result)
        self.assertTrue(self.dest_file.exists())
    
    def test_safe_copy_file_nonexistent_source(self):
        """Test copying non-existent source file"""
        non_existent = self.temp_dir / "nonexistent.txt"
        
        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            safe_copy_file(non_existent, self.dest_file)
    
    def test_safe_copy_file_permission_error(self):
        """Test copying with permission errors"""
        restricted_dest = Path("/root/restricted.txt")
        
        # This should raise PermissionError
        with self.assertRaises(PermissionError):
            safe_copy_file(self.source_file, restricted_dest)
    
    def test_safe_copy_file_creates_dest_directory(self):
        """Test that safe_copy_file creates destination directory"""
        nested_dest = self.temp_dir / "nested" / "dir" / "file.txt"
        
        result = safe_copy_file(self.source_file, nested_dest)
        
        self.assertTrue(result)
        self.assertTrue(nested_dest.exists())
        self.assertTrue(nested_dest.parent.exists())


class TestSafeRemoveFile(unittest.TestCase):
    """Test cases for safe_remove_file function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.txt"
        self.test_file.write_text("test content")
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_safe_remove_file_success(self):
        """Test successful file removal"""
        # This will fail until safe_remove_file is implemented
        result = safe_remove_file(self.test_file)
        
        self.assertTrue(result)
        self.assertFalse(self.test_file.exists())
    
    def test_safe_remove_file_nonexistent(self):
        """Test removing non-existent file"""
        non_existent = self.temp_dir / "nonexistent.txt"
        
        # This should return False for non-existent files
        result = safe_remove_file(non_existent)
        
        self.assertFalse(result)
    
    def test_safe_remove_file_permission_error(self):
        """Test removing file with permission errors"""
        restricted_file = Path("/root/restricted.txt")
        
        # This should raise PermissionError
        with self.assertRaises(PermissionError):
            safe_remove_file(restricted_file)
    
    def test_safe_remove_file_directory(self):
        """Test attempting to remove a directory"""
        test_dir = self.temp_dir / "testdir"
        test_dir.mkdir()
        
        # This should raise OSError (is a directory)
        with self.assertRaises(OSError):
            safe_remove_file(test_dir)


class TestGetFileSize(unittest.TestCase):
    """Test cases for get_file_size function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.txt"
        self.test_content = "Hello, World!" * 100  # 1300 bytes
        self.test_file.write_text(self.test_content)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_get_file_size_success(self):
        """Test getting file size successfully"""
        # This will fail until get_file_size is implemented
        size = get_file_size(self.test_file)
        
        self.assertIsInstance(size, int)
        self.assertEqual(size, len(self.test_content.encode('utf-8')))
    
    def test_get_file_size_empty_file(self):
        """Test getting size of empty file"""
        empty_file = self.temp_dir / "empty.txt"
        empty_file.write_text("")
        
        size = get_file_size(empty_file)
        
        self.assertEqual(size, 0)
    
    def test_get_file_size_nonexistent_file(self):
        """Test getting size of non-existent file"""
        non_existent = self.temp_dir / "nonexistent.txt"
        
        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            get_file_size(non_existent)
    
    def test_get_file_size_directory(self):
        """Test getting size of directory"""
        test_dir = self.temp_dir / "testdir"
        test_dir.mkdir()
        
        # This should raise OSError (is a directory)
        with self.assertRaises(OSError):
            get_file_size(test_dir)


class TestGetRelativePath(unittest.TestCase):
    """Test cases for get_relative_path function"""
    
    def test_get_relative_path_success(self):
        """Test getting relative path successfully"""
        base_path = Path("/home/user/project")
        file_path = Path("/home/user/project/src/main.py")
        
        # This will fail until get_relative_path is implemented
        relative = get_relative_path(file_path, base_path)
        
        self.assertIsInstance(relative, Path)
        self.assertEqual(relative, Path("src/main.py"))
    
    def test_get_relative_path_same_path(self):
        """Test getting relative path when file and base are the same"""
        base_path = Path("/home/user/project")
        file_path = Path("/home/user/project")
        
        relative = get_relative_path(file_path, base_path)
        
        self.assertEqual(relative, Path("."))
    
    def test_get_relative_path_not_under_base(self):
        """Test getting relative path when file is not under base"""
        base_path = Path("/home/user/project")
        file_path = Path("/home/other/file.txt")
        
        # This should raise ValueError
        with self.assertRaises(ValueError):
            get_relative_path(file_path, base_path)
    
    def test_get_relative_path_nested_deep(self):
        """Test getting relative path with deep nesting"""
        base_path = Path("/home/user")
        file_path = Path("/home/user/project/src/deep/nested/file.txt")
        
        relative = get_relative_path(file_path, base_path)
        
        self.assertEqual(relative, Path("project/src/deep/nested/file.txt"))


class TestEnsureDirectoryExists(unittest.TestCase):
    """Test cases for ensure_directory_exists function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory_exists_create_new(self):
        """Test creating new directory"""
        new_dir = self.temp_dir / "new" / "nested" / "dir"
        
        # This will fail until ensure_directory_exists is implemented
        ensure_directory_exists(new_dir)
        
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())
    
    def test_ensure_directory_exists_already_exists(self):
        """Test with directory that already exists"""
        existing_dir = self.temp_dir / "existing"
        existing_dir.mkdir()
        
        # This should not raise an error
        ensure_directory_exists(existing_dir)
        
        self.assertTrue(existing_dir.exists())
        self.assertTrue(existing_dir.is_dir())
    
    def test_ensure_directory_exists_permission_error(self):
        """Test creating directory with permission errors"""
        restricted_dir = Path("/root/restricted/dir")
        
        # This should raise PermissionError
        with self.assertRaises(PermissionError):
            ensure_directory_exists(restricted_dir)
    
    def test_ensure_directory_exists_file_exists(self):
        """Test when a file exists with the same name"""
        file_path = self.temp_dir / "file.txt"
        file_path.write_text("content")
        
        # This should raise OSError (file exists)
        with self.assertRaises(OSError):
            ensure_directory_exists(file_path)


class TestIsPathSafe(unittest.TestCase):
    """Test cases for is_path_safe function"""
    
    def test_is_path_safe_valid_path(self):
        """Test path safety with valid path"""
        base_path = Path("/home/user/project")
        safe_path = Path("/home/user/project/src/file.txt")
        
        # This will fail until is_path_safe is implemented
        result = is_path_safe(safe_path, base_path)
        
        self.assertTrue(result)
    
    def test_is_path_safe_same_path(self):
        """Test path safety with same path"""
        base_path = Path("/home/user/project")
        same_path = Path("/home/user/project")
        
        result = is_path_safe(same_path, base_path)
        
        self.assertTrue(result)
    
    def test_is_path_safe_parent_escape(self):
        """Test path safety with parent directory escape"""
        base_path = Path("/home/user/project")
        escape_path = Path("/home/user/project/../../../etc/passwd")
        
        result = is_path_safe(escape_path, base_path)
        
        self.assertFalse(result)
    
    def test_is_path_safe_outside_base(self):
        """Test path safety with path outside base"""
        base_path = Path("/home/user/project")
        outside_path = Path("/home/other/file.txt")
        
        result = is_path_safe(outside_path, base_path)
        
        self.assertFalse(result)
    
    def test_is_path_safe_relative_path(self):
        """Test path safety with relative path"""
        base_path = Path("/home/user/project")
        relative_path = Path("src/file.txt")
        
        result = is_path_safe(relative_path, base_path)
        
        self.assertTrue(result)


class TestFormatFileSize(unittest.TestCase):
    """Test cases for format_file_size function"""
    
    def test_format_file_size_bytes(self):
        """Test formatting file size in bytes"""
        # This will fail until format_file_size is implemented
        result = format_file_size(512)
        
        self.assertEqual(result, "512 B")
    
    def test_format_file_size_kilobytes(self):
        """Test formatting file size in kilobytes"""
        result = format_file_size(1536)  # 1.5 KB
        
        self.assertEqual(result, "1.5 KB")
    
    def test_format_file_size_megabytes(self):
        """Test formatting file size in megabytes"""
        result = format_file_size(2097152)  # 2 MB
        
        self.assertEqual(result, "2.0 MB")
    
    def test_format_file_size_gigabytes(self):
        """Test formatting file size in gigabytes"""
        result = format_file_size(1073741824)  # 1 GB
        
        self.assertEqual(result, "1.0 GB")
    
    def test_format_file_size_zero(self):
        """Test formatting zero file size"""
        result = format_file_size(0)
        
        self.assertEqual(result, "0 B")
    
    def test_format_file_size_negative(self):
        """Test formatting negative file size"""
        # This should handle negative sizes gracefully
        result = format_file_size(-100)
        
        self.assertEqual(result, "0 B")  # or raise ValueError


class TestGetSyncSummary(unittest.TestCase):
    """Test cases for get_sync_summary function"""
    
    def test_get_sync_summary_success(self):
        """Test generating sync summary successfully"""
        copied_files = [
            Path("/dest/file1.txt"),
            Path("/dest/file2.txt"),
            Path("/dest/subdir/file3.txt")
        ]
        deleted_files = [
            Path("/dest/old_file.txt"),
            Path("/dest/temp.log")
        ]
        
        # This will fail until get_sync_summary is implemented
        summary = get_sync_summary(copied_files, deleted_files)
        
        self.assertIsInstance(summary, str)
        self.assertIn("3", summary)  # 3 files copied
        self.assertIn("2", summary)  # 2 files deleted
        self.assertIn("copied", summary.lower())
        self.assertIn("deleted", summary.lower())
    
    def test_get_sync_summary_empty_lists(self):
        """Test generating sync summary with empty lists"""
        summary = get_sync_summary([], [])
        
        self.assertIsInstance(summary, str)
        self.assertIn("0", summary)
        self.assertIn("copied", summary.lower())
        self.assertIn("deleted", summary.lower())
    
    def test_get_sync_summary_only_copied(self):
        """Test generating sync summary with only copied files"""
        copied_files = [Path("/dest/file1.txt")]
        deleted_files = []
        
        summary = get_sync_summary(copied_files, deleted_files)
        
        self.assertIsInstance(summary, str)
        self.assertIn("1", summary)
        self.assertIn("0", summary)
    
    def test_get_sync_summary_only_deleted(self):
        """Test generating sync summary with only deleted files"""
        copied_files = []
        deleted_files = [Path("/dest/old_file.txt")]
        
        summary = get_sync_summary(copied_files, deleted_files)
        
        self.assertIsInstance(summary, str)
        self.assertIn("0", summary)
        self.assertIn("1", summary)


if __name__ == "__main__":
    unittest.main()