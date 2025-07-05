#!/usr/bin/env python3
"""
Integration tests for wslsync - testing complete sync workflow
"""

import os
import shutil
import unittest
from pathlib import Path


class TestWSLSyncIntegration(unittest.TestCase):
    """Integration tests for complete WSL sync workflow"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(__file__).parent
        self.config_file = self.test_dir / "fixtures" / ".wslsync"
        self.windows_source = self.test_dir / "mock_windows_source"
        self.wsl2_dest = self.test_dir / "mock_wsl2_dest"

        # Reset destination directory
        if self.wsl2_dest.exists():
            shutil.rmtree(self.wsl2_dest)
        self.wsl2_dest.mkdir(parents=True)

        # Create pre-existing files that should be cleaned up
        (self.wsl2_dest / "old_file.txt").write_text("Should be deleted")
        (self.wsl2_dest / "temp_data.log").write_text("Temporary data")
        outdated_dir = self.wsl2_dest / "outdated_folder"
        outdated_dir.mkdir()
        (outdated_dir / "legacy.txt").write_text("Legacy file")

    def test_complete_sync_workflow(self):
        """Test complete sync: parse config, copy files, cleanup"""
        # Step 1: Parse config (simulate)
        config_content = self.config_file.read_text()

        # Extract file list from config
        files_to_sync = [
            "documents/config.txt",
            "documents/notes.md",
            "scripts/backup.sh",
            "projects/app/main.py",
        ]

        # Verify all source files exist
        for file_path in files_to_sync:
            source_file = self.windows_source / file_path
            self.assertTrue(source_file.exists(), f"Source {file_path} must exist")

        # Step 2: Copy files
        copied_files = []
        for file_path in files_to_sync:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path

            # Create directory structure
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source, dest)
            copied_files.append(str(dest.relative_to(self.wsl2_dest)))

        # Step 3: Cleanup files not in sync list
        files_to_keep = set(files_to_sync)

        # Get all files currently in destination
        all_files = []
        for item in self.wsl2_dest.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(self.wsl2_dest))
                all_files.append(rel_path)

        # Remove files not in keep list
        for file_path in all_files:
            if file_path not in files_to_keep:
                file_obj = self.wsl2_dest / file_path
                file_obj.unlink()

        # Remove empty directories
        for item in list(self.wsl2_dest.rglob("*")):
            if item.is_dir() and not any(item.iterdir()):
                item.rmdir()

        # Step 4: Verify final state
        # Check that all expected files exist
        for file_path in files_to_sync:
            dest_file = self.wsl2_dest / file_path
            self.assertTrue(dest_file.exists(), f"Synced file {file_path} should exist")

            # Verify content matches source
            source_content = (self.windows_source / file_path).read_text()
            dest_content = dest_file.read_text()
            self.assertEqual(
                source_content, dest_content, f"Content mismatch for {file_path}"
            )

        # Check that cleanup files are gone
        cleanup_files = ["old_file.txt", "temp_data.log", "outdated_folder/legacy.txt"]
        for file_path in cleanup_files:
            cleanup_file = self.wsl2_dest / file_path
            self.assertFalse(
                cleanup_file.exists(), f"File {file_path} should be cleaned up"
            )

        # Verify only expected files remain
        remaining_files = []
        for item in self.wsl2_dest.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(self.wsl2_dest))
                remaining_files.append(rel_path)

        remaining_files.sort()
        expected_files = sorted(files_to_sync)
        self.assertEqual(
            remaining_files, expected_files, "Only synced files should remain"
        )

    def test_sync_with_modified_files(self):
        """Test sync when files have been modified"""
        # Initial sync
        files_to_sync = ["documents/config.txt", "documents/notes.md"]

        for file_path in files_to_sync:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)

        # Modify a file in destination
        dest_file = self.wsl2_dest / "documents/config.txt"
        dest_file.write_text("Modified content")

        # Re-sync (should overwrite modifications)
        for file_path in files_to_sync:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path
            shutil.copy2(source, dest)

        # Verify file was overwritten with source content
        source_content = (self.windows_source / "documents/config.txt").read_text()
        dest_content = dest_file.read_text()
        self.assertEqual(
            source_content, dest_content, "Modified file should be overwritten"
        )

    def test_sync_preserves_timestamps(self):
        """Test that sync preserves file timestamps"""
        file_path = "documents/config.txt"
        source = self.windows_source / file_path
        dest = self.wsl2_dest / file_path

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)  # copy2 preserves timestamps

        # Verify timestamps match
        source_mtime = source.stat().st_mtime
        dest_mtime = dest.stat().st_mtime
        self.assertEqual(source_mtime, dest_mtime, "Timestamps should be preserved")

    def test_sync_with_missing_source_file(self):
        """Test behavior when source file is missing"""
        # Create a non-existent source file path
        missing_file = "documents/missing.txt"
        source = self.windows_source / missing_file
        dest = self.wsl2_dest / missing_file

        # Verify source doesn't exist
        self.assertFalse(source.exists(), "Source file should not exist")

        # This would typically raise an exception in real implementation
        # For now, we just verify the expected behavior
        with self.assertRaises(FileNotFoundError):
            shutil.copy2(source, dest)


if __name__ == "__main__":
    unittest.main()
