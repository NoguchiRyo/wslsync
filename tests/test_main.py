#!/usr/bin/env python3
"""
TDD tests for __main__.py module
"""

import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from wslsync.__main__ import (
    create_argument_parser,
    main,
    run_sync,
    show_version,
    validate_config_command,
)
from wslsync.config import WSLSyncConfig


class TestCreateArgumentParser(unittest.TestCase):
    """Test cases for create_argument_parser function"""

    def test_create_argument_parser_returns_parser(self):
        """Test that create_argument_parser returns ArgumentParser"""
        # This will fail until create_argument_parser is implemented
        parser = create_argument_parser()

        self.assertIsNotNone(parser)
        self.assertEqual(parser.__class__.__name__, "ArgumentParser")

    def test_argument_parser_has_config_option(self):
        """Test that parser has config file option"""
        parser = create_argument_parser()

        # Test parsing with config option
        args = parser.parse_args(["--config", "/path/to/.wslsync"])

        self.assertEqual(args.config, "/path/to/.wslsync")

    def test_argument_parser_has_dry_run_option(self):
        """Test that parser has dry-run option"""
        parser = create_argument_parser()

        # Test parsing with dry-run option
        args = parser.parse_args(["--dry-run"])

        self.assertTrue(args.dry_run)

    def test_argument_parser_has_verbose_option(self):
        """Test that parser has verbose option"""
        parser = create_argument_parser()

        # Test parsing with verbose option
        args = parser.parse_args(["--verbose"])

        self.assertTrue(args.verbose)

    def test_argument_parser_has_validate_config_option(self):
        """Test that parser has validate-config option"""
        parser = create_argument_parser()

        # Test parsing with validate-config option
        args = parser.parse_args(["--validate-config"])

        self.assertTrue(args.validate_config)

    def test_argument_parser_has_version_option(self):
        """Test that parser has version option"""
        parser = create_argument_parser()

        # Test parsing with version option
        args = parser.parse_args(["--version"])

        self.assertTrue(args.version)

    def test_argument_parser_default_values(self):
        """Test argument parser default values"""
        parser = create_argument_parser()

        # Test parsing with no arguments
        args = parser.parse_args([])

        self.assertIsNone(args.config)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.verbose)
        self.assertFalse(args.validate_config)
        self.assertFalse(args.version)


class TestMain(unittest.TestCase):
    """Test cases for main function"""

    @patch("wslsync.__main__.run_sync")
    @patch("wslsync.__main__.create_argument_parser")
    def test_main_default_behavior(self, mock_parser, mock_run_sync):
        """Test main function default behavior"""
        # Mock argument parser
        mock_args = MagicMock()
        mock_args.config = None
        mock_args.dry_run = False
        mock_args.verbose = False
        mock_args.validate_config = False
        mock_args.version = False

        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_run_sync.return_value = 0

        # This will fail until main is implemented
        exit_code = main([])

        self.assertEqual(exit_code, 0)
        mock_run_sync.assert_called_once()

    @patch("wslsync.__main__.validate_config_command")
    @patch("wslsync.__main__.create_argument_parser")
    def test_main_validate_config_mode(self, mock_parser, mock_validate):
        """Test main function in validate-config mode"""
        # Mock argument parser
        mock_args = MagicMock()
        mock_args.config = "/path/to/.wslsync"
        mock_args.validate_config = True
        mock_args.version = False

        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_validate.return_value = 0

        exit_code = main([])

        self.assertEqual(exit_code, 0)
        mock_validate.assert_called_once_with(Path("/path/to/.wslsync"))

    @patch("wslsync.__main__.show_version")
    @patch("wslsync.__main__.create_argument_parser")
    def test_main_version_mode(self, mock_parser, mock_show_version):
        """Test main function in version mode"""
        # Mock argument parser
        mock_args = MagicMock()
        mock_args.version = True

        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        exit_code = main([])

        self.assertEqual(exit_code, 0)
        mock_show_version.assert_called_once()

    @patch("wslsync.__main__.create_argument_parser")
    def test_main_with_exception(self, mock_parser):
        """Test main function handling exceptions"""
        # Mock argument parser to raise exception
        mock_parser.side_effect = Exception("Test exception")

        exit_code = main([])

        self.assertNotEqual(exit_code, 0)  # Should return non-zero on error

    @patch("wslsync.__main__.run_sync")
    @patch("wslsync.__main__.create_argument_parser")
    def test_main_custom_config_path(self, mock_parser, mock_run_sync):
        """Test main function with custom config path"""
        # Mock argument parser
        mock_args = MagicMock()
        mock_args.config = "/custom/path/.wslsync"
        mock_args.dry_run = False
        mock_args.verbose = False
        mock_args.validate_config = False
        mock_args.version = False

        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        mock_run_sync.return_value = 0

        exit_code = main([])

        self.assertEqual(exit_code, 0)
        mock_run_sync.assert_called_once()
        # Verify custom config path is used
        args, kwargs = mock_run_sync.call_args
        self.assertEqual(args[0], Path("/custom/path/.wslsync"))


class TestRunSync(unittest.TestCase):
    """Test cases for run_sync function"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / ".wslsync"
        self.config_file.write_text(
            """
windows_base = /mnt/c/source
wsl2_base = /home/user/dest
files = ["file1.txt", "file2.txt"]
"""
        )

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("wslsync.__main__.WSLSyncEngine")
    @patch("wslsync.__main__.parse_config")
    @patch("wslsync.__main__.setup_logging")
    def test_run_sync_success(
        self, mock_setup_logging, mock_parse_config, mock_engine_class
    ):
        """Test successful sync run"""
        # Mock dependencies
        mock_config = MagicMock()
        mock_parse_config.return_value = mock_config

        mock_engine = MagicMock()
        mock_engine.sync.return_value = None
        mock_engine_class.return_value = mock_engine

        # This will fail until run_sync is implemented
        exit_code = run_sync(self.config_file, dry_run=False, verbose=False)

        self.assertEqual(exit_code, 0)
        mock_parse_config.assert_called_once_with(self.config_file)
        mock_engine_class.assert_called_once_with(mock_config)
        mock_engine.sync.assert_called_once()

    @patch("wslsync.__main__.setup_logging")
    def test_run_sync_nonexistent_config(self, mock_setup_logging):
        """Test sync run with non-existent config file"""
        non_existent_config = self.temp_dir / "nonexistent.wslsync"

        exit_code = run_sync(non_existent_config, dry_run=False, verbose=False)

        self.assertNotEqual(exit_code, 0)  # Should return non-zero on error

    @patch("wslsync.__main__.WSLSyncEngine")
    @patch("wslsync.__main__.parse_config")
    @patch("wslsync.__main__.setup_logging")
    def test_run_sync_dry_run_mode(
        self, mock_setup_logging, mock_parse_config, mock_engine_class
    ):
        """Test sync run in dry-run mode"""
        # Mock dependencies
        mock_config = MagicMock()
        mock_parse_config.return_value = mock_config

        mock_engine = MagicMock()
        mock_engine.get_source_files.return_value = [
            Path("file1.txt"),
            Path("file2.txt"),
        ]
        mock_engine.get_destination_files.return_value = [Path("old_file.txt")]
        mock_engine_class.return_value = mock_engine

        exit_code = run_sync(self.config_file, dry_run=True, verbose=False)

        self.assertEqual(exit_code, 0)
        # In dry-run mode, sync() should not be called
        mock_engine.sync.assert_not_called()
        # But analysis methods should be called
        mock_engine.get_source_files.assert_called_once()
        mock_engine.get_destination_files.assert_called_once()

    @patch("wslsync.__main__.setup_logging")
    def test_run_sync_verbose_mode(self, mock_setup_logging):
        """Test sync run in verbose mode"""
        exit_code = run_sync(self.config_file, dry_run=False, verbose=True)

        # Verify verbose logging was set up
        mock_setup_logging.assert_called_once()
        args, kwargs = mock_setup_logging.call_args
        self.assertEqual(args[0], "DEBUG")  # Verbose should set DEBUG level

    @patch("wslsync.__main__.WSLSyncEngine")
    @patch("wslsync.__main__.parse_config")
    @patch("wslsync.__main__.setup_logging")
    def test_run_sync_engine_exception(
        self, mock_setup_logging, mock_parse_config, mock_engine_class
    ):
        """Test sync run when engine raises exception"""
        # Mock dependencies
        mock_config = MagicMock()
        mock_parse_config.return_value = mock_config

        mock_engine = MagicMock()
        mock_engine.sync.side_effect = Exception("Sync failed")
        mock_engine_class.return_value = mock_engine

        exit_code = run_sync(self.config_file, dry_run=False, verbose=False)

        self.assertNotEqual(exit_code, 0)  # Should return non-zero on error


class TestValidateConfigCommand(unittest.TestCase):
    """Test cases for validate_config_command function"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.valid_config = self.temp_dir / "valid.wslsync"
        self.valid_config.write_text(
            """
windows_base = /mnt/c/source
wsl2_base = /home/user/dest
files = ["file1.txt", "file2.txt"]
"""
        )

        self.invalid_config = self.temp_dir / "invalid.wslsync"
        self.invalid_config.write_text(
            """
windows_base = /mnt/c/source
# missing wsl2_base
files = ["file1.txt"]
"""
        )

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("wslsync.__main__.validate_config")
    @patch("wslsync.__main__.parse_config")
    def test_validate_config_command_valid(
        self, mock_parse_config, mock_validate_config
    ):
        """Test validate_config_command with valid config"""
        mock_config = MagicMock()
        mock_parse_config.return_value = mock_config
        mock_validate_config.return_value = True

        # This will fail until validate_config_command is implemented
        exit_code = validate_config_command(self.valid_config)

        self.assertEqual(exit_code, 0)
        mock_parse_config.assert_called_once_with(self.valid_config)
        mock_validate_config.assert_called_once_with(mock_config)

    @patch("wslsync.__main__.validate_config")
    @patch("wslsync.__main__.parse_config")
    def test_validate_config_command_invalid(
        self, mock_parse_config, mock_validate_config
    ):
        """Test validate_config_command with invalid config"""
        mock_config = MagicMock()
        mock_parse_config.return_value = mock_config
        mock_validate_config.side_effect = ValueError("Invalid config")

        exit_code = validate_config_command(self.invalid_config)

        self.assertNotEqual(exit_code, 0)  # Should return non-zero for invalid config

    def test_validate_config_command_nonexistent_file(self):
        """Test validate_config_command with non-existent file"""
        non_existent = self.temp_dir / "nonexistent.wslsync"

        exit_code = validate_config_command(non_existent)

        self.assertNotEqual(exit_code, 0)  # Should return non-zero for missing file

    @patch("wslsync.__main__.parse_config")
    def test_validate_config_command_parse_error(self, mock_parse_config):
        """Test validate_config_command with parse error"""
        mock_parse_config.side_effect = ValueError("Parse error")

        exit_code = validate_config_command(self.valid_config)

        self.assertNotEqual(exit_code, 0)  # Should return non-zero for parse error


class TestShowVersion(unittest.TestCase):
    """Test cases for show_version function"""

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_version_output(self, mock_stdout):
        """Test show_version produces output"""
        # This will fail until show_version is implemented
        show_version()

        output = mock_stdout.getvalue()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)
        self.assertIn("wslsync", output.lower())

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_version_includes_version_number(self, mock_stdout):
        """Test show_version includes version number"""
        show_version()

        output = mock_stdout.getvalue()
        # Should contain some version-like pattern (numbers and dots)
        self.assertRegex(output, r"\d+\.\d+\.\d+")

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_version_includes_description(self, mock_stdout):
        """Test show_version includes description"""
        show_version()

        output = mock_stdout.getvalue()
        # Should contain descriptive text
        self.assertIn("WSL", output)
        self.assertIn("sync", output.lower())


class TestMainIntegration(unittest.TestCase):
    """Integration tests for main function"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / ".wslsync"
        self.config_file.write_text(
            """
windows_base = /mnt/c/source
wsl2_base = /home/user/dest
files = ["file1.txt", "file2.txt"]
"""
        )

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("wslsync.__main__.run_sync")
    def test_main_integration_sync_mode(self, mock_run_sync):
        """Test main function integration in sync mode"""
        mock_run_sync.return_value = 0

        # Test command line arguments
        args = ["--config", str(self.config_file), "--dry-run", "--verbose"]

        exit_code = main(args)

        self.assertEqual(exit_code, 0)
        mock_run_sync.assert_called_once()

        # Verify arguments were passed correctly
        call_args = mock_run_sync.call_args
        self.assertEqual(call_args[0][0], self.config_file)  # config_path
        self.assertTrue(call_args[1]["dry_run"])
        self.assertTrue(call_args[1]["verbose"])

    @patch("wslsync.__main__.validate_config_command")
    def test_main_integration_validate_mode(self, mock_validate):
        """Test main function integration in validate mode"""
        mock_validate.return_value = 0

        # Test command line arguments
        args = ["--config", str(self.config_file), "--validate-config"]

        exit_code = main(args)

        self.assertEqual(exit_code, 0)
        mock_validate.assert_called_once_with(self.config_file)

    @patch("wslsync.__main__.show_version")
    def test_main_integration_version_mode(self, mock_show_version):
        """Test main function integration in version mode"""
        # Test command line arguments
        args = ["--version"]

        exit_code = main(args)

        self.assertEqual(exit_code, 0)
        mock_show_version.assert_called_once()


if __name__ == "__main__":
    unittest.main()
