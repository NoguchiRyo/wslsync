#!/usr/bin/env python3
"""
TDD tests for config.py module
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from wslsync.config import (
    WSLSyncConfig,
    get_default_config_path,
    parse_config,
    validate_config,
)


class TestWSLSyncConfig(unittest.TestCase):
    """Test cases for WSLSyncConfig dataclass"""

    def test_wslsync_config_creation(self):
        """Test creating WSLSyncConfig instance"""
        # This will fail until WSLSyncConfig is properly implemented
        config = WSLSyncConfig(
            windows_base=Path("/mnt/c/source"),
            wsl2_base=Path("/home/user/dest"),
            files=["file1.txt", "file2.txt"],
        )

        self.assertEqual(config.windows_base, Path("/mnt/c/source"))
        self.assertEqual(config.wsl2_base, Path("/home/user/dest"))
        self.assertEqual(config.files, ["file1.txt", "file2.txt"])

    def test_wslsync_config_defaults(self):
        """Test WSLSyncConfig with default values"""
        config = WSLSyncConfig()

        # Test default values (will fail until implemented)
        self.assertIsNone(config.windows_base)
        self.assertIsNone(config.wsl2_base)
        self.assertEqual(config.files, [])


class TestParseConfig(unittest.TestCase):
    """Test cases for parse_config function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config_content = """# Test .wslsync config
windows_base = /mnt/c/source
wsl2_base = /home/user/dest
files = [
    "documents/config.txt",
    "documents/notes.md",
    "scripts/backup.sh"
]"""

        self.invalid_config_content = """# Invalid config
windows_base = /mnt/c/source
# missing wsl2_base
files = ["file1.txt"]"""

    def test_parse_valid_config_file(self):
        """Test parsing a valid config file"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".wslsync", delete=False
        ) as f:
            f.write(self.test_config_content)
            f.flush()

            config_path = Path(f.name)

            # This will fail until parse_config is implemented
            config = parse_config(config_path)

            self.assertIsInstance(config, WSLSyncConfig)
            self.assertEqual(config.windows_base, Path("/mnt/c/source"))
            self.assertEqual(config.wsl2_base, Path("/home/user/dest"))
            self.assertEqual(len(config.files), 3)
            self.assertIn("documents/config.txt", config.files)

        # Clean up
        config_path.unlink()

    def test_parse_nonexistent_config_file(self):
        """Test parsing a non-existent config file"""
        non_existent_path = Path("/non/existent/path/.wslsync")

        # This should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            parse_config(non_existent_path)

    def test_parse_invalid_config_format(self):
        """Test parsing config with invalid format"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".wslsync", delete=False
        ) as f:
            f.write(self.invalid_config_content)
            f.flush()

            config_path = Path(f.name)

            # This should raise ValueError for invalid format
            with self.assertRaises(ValueError):
                parse_config(config_path)

        # Clean up
        config_path.unlink()

    def test_parse_empty_config_file(self):
        """Test parsing empty config file"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".wslsync", delete=False
        ) as f:
            f.write("")
            f.flush()

            config_path = Path(f.name)

            # This should raise ValueError for empty file
            with self.assertRaises(ValueError):
                parse_config(config_path)

        # Clean up
        config_path.unlink()

    def test_parse_config_with_comments(self):
        """Test parsing config with comments and whitespace"""
        config_with_comments = """# This is a comment
# Another comment
windows_base = /mnt/c/source  # inline comment
wsl2_base = /home/user/dest

# Files section
files = [
    "file1.txt",  # first file
    "file2.txt"   # second file
]"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".wslsync", delete=False
        ) as f:
            f.write(config_with_comments)
            f.flush()

            config_path = Path(f.name)

            # This will fail until parse_config handles comments
            config = parse_config(config_path)

            self.assertEqual(config.windows_base, Path("/mnt/c/source"))
            self.assertEqual(config.wsl2_base, Path("/home/user/dest"))
            self.assertEqual(len(config.files), 2)

        # Clean up
        config_path.unlink()


class TestValidateConfig(unittest.TestCase):
    """Test cases for validate_config function"""

    def test_validate_valid_config(self):
        """Test validating a valid configuration"""
        config = WSLSyncConfig(
            windows_base=Path("/mnt/c/source"),
            wsl2_base=Path("/home/user/dest"),
            files=["file1.txt", "file2.txt"],
        )

        # This will fail until validate_config is implemented
        result = validate_config(config)
        self.assertTrue(result)

    def test_validate_config_missing_windows_base(self):
        """Test validating config with missing windows_base"""
        config = WSLSyncConfig(
            windows_base=None, wsl2_base=Path("/home/user/dest"), files=["file1.txt"]
        )

        # This should raise ValueError
        with self.assertRaises(ValueError) as context:
            validate_config(config)

        self.assertIn("windows_base", str(context.exception))

    def test_validate_config_missing_wsl2_base(self):
        """Test validating config with missing wsl2_base"""
        config = WSLSyncConfig(
            windows_base=Path("/mnt/c/source"), wsl2_base=None, files=["file1.txt"]
        )

        # This should raise ValueError
        with self.assertRaises(ValueError) as context:
            validate_config(config)

        self.assertIn("wsl2_base", str(context.exception))

    def test_validate_config_empty_files_list(self):
        """Test validating config with empty files list"""
        config = WSLSyncConfig(
            windows_base=Path("/mnt/c/source"),
            wsl2_base=Path("/home/user/dest"),
            files=[],
        )

        # This should raise ValueError
        with self.assertRaises(ValueError) as context:
            validate_config(config)

        self.assertIn("files", str(context.exception))

    def test_validate_config_invalid_path_format(self):
        """Test validating config with invalid path format"""
        config = WSLSyncConfig(
            windows_base=Path(""),  # Empty path
            wsl2_base=Path("/home/user/dest"),
            files=["file1.txt"],
        )

        # This should raise ValueError
        with self.assertRaises(ValueError) as context:
            validate_config(config)

        self.assertIn("path", str(context.exception).lower())

    def test_validate_config_duplicate_files(self):
        """Test validating config with duplicate files"""
        config = WSLSyncConfig(
            windows_base=Path("/mnt/c/source"),
            wsl2_base=Path("/home/user/dest"),
            files=["file1.txt", "file1.txt", "file2.txt"],
        )

        # This should raise ValueError for duplicates
        with self.assertRaises(ValueError) as context:
            validate_config(config)

        self.assertIn("duplicate", str(context.exception).lower())


class TestGetDefaultConfigPath(unittest.TestCase):
    """Test cases for get_default_config_path function"""

    @patch("wslsync.config.Path.home")
    def test_get_default_config_path(self, mock_home):
        """Test getting default config path"""
        mock_home.return_value = Path("/home/testuser")

        # This will fail until get_default_config_path is implemented
        default_path = get_default_config_path()

        expected_path = Path("/home/testuser/.wslsync")
        self.assertEqual(default_path, expected_path)

    @patch("wslsync.config.Path.home")
    def test_get_default_config_path_different_home(self, mock_home):
        """Test getting default config path with different home directory"""
        mock_home.return_value = Path("/home/anotheruser")

        default_path = get_default_config_path()

        expected_path = Path("/home/anotheruser/.wslsync")
        self.assertEqual(default_path, expected_path)

    def test_get_default_config_path_returns_path_object(self):
        """Test that get_default_config_path returns a Path object"""
        default_path = get_default_config_path()

        self.assertIsInstance(default_path, Path)
        self.assertTrue(str(default_path).endswith(".wslsync"))


if __name__ == "__main__":
    unittest.main()
