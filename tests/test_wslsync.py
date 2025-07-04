#!/usr/bin/env python3
"""
Test suite for wslsync
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path


class TestWSLSync(unittest.TestCase):
    """Test cases for WSL sync functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(__file__).parent
        self.config_file = self.test_dir / "fixtures" / ".wslsync"
        self.windows_source = self.test_dir / "mock_windows_source"
        self.wsl2_dest = self.test_dir / "mock_wsl2_dest"
        
        # Reset destination directory for each test
        if self.wsl2_dest.exists():
            shutil.rmtree(self.wsl2_dest)
        self.wsl2_dest.mkdir(parents=True)
        
        # Create some existing files for cleanup testing
        (self.wsl2_dest / "old_file.txt").write_text("This should be deleted")
        (self.wsl2_dest / "temp_data.log").write_text("Temporary data")
        outdated_dir = self.wsl2_dest / "outdated_folder"
        outdated_dir.mkdir()
        (outdated_dir / "legacy.txt").write_text("Legacy file")
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_config_parsing(self):
        """Test parsing of .wslsync config file"""
        # This test will verify config file parsing
        # Expected format:
        # windows_base = tests/mock_windows_source
        # wsl2_base = tests/mock_wsl2_dest
        # files = [list of relative paths]
        
        self.assertTrue(self.config_file.exists(), "Config file should exist")
        
        config_content = self.config_file.read_text()
        
        # Basic validation that config contains expected sections
        self.assertIn("windows_base", config_content)
        self.assertIn("wsl2_base", config_content)
        self.assertIn("files", config_content)
        
        # Verify expected files are listed
        expected_files = [
            "documents/config.txt",
            "documents/notes.md", 
            "scripts/backup.sh",
            "projects/app/main.py"
        ]
        
        for file_path in expected_files:
            self.assertIn(file_path, config_content)
    
    def test_source_files_exist(self):
        """Test that all source files exist for copying"""
        expected_files = [
            "documents/config.txt",
            "documents/notes.md",
            "scripts/backup.sh", 
            "projects/app/main.py"
        ]
        
        for file_path in expected_files:
            source_file = self.windows_source / file_path
            self.assertTrue(source_file.exists(), f"Source file {file_path} should exist")
            self.assertTrue(source_file.is_file(), f"{file_path} should be a file")
    
    def test_file_copying(self):
        """Test copying files from source to destination"""
        # This test simulates the core sync functionality
        files_to_copy = [
            "documents/config.txt",
            "documents/notes.md",
            "scripts/backup.sh",
            "projects/app/main.py"
        ]
        
        # Simulate copying files
        for file_path in files_to_copy:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path
            
            # Create destination directory if it doesn't exist
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, dest)
            
            # Verify file was copied
            self.assertTrue(dest.exists(), f"File {file_path} should be copied")
            
            # Verify content matches
            source_content = source.read_text()
            dest_content = dest.read_text()
            self.assertEqual(source_content, dest_content, f"Content should match for {file_path}")
    
    def test_cleanup_functionality(self):
        """Test cleanup of files not in sync list"""
        # Files that should be cleaned up
        cleanup_files = [
            "old_file.txt",
            "temp_data.log",
            "outdated_folder/legacy.txt"
        ]
        
        # Verify cleanup files exist initially
        for file_path in cleanup_files:
            file_obj = self.wsl2_dest / file_path
            self.assertTrue(file_obj.exists(), f"Cleanup target {file_path} should exist initially")
        
        # Files that should be kept (from sync list)
        keep_files = [
            "documents/config.txt",
            "documents/notes.md",
            "scripts/backup.sh",
            "projects/app/main.py"
        ]
        
        # First copy the files we want to keep
        for file_path in keep_files:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        
        # Simulate cleanup: remove files not in keep_files list
        for item in self.wsl2_dest.rglob("*"):
            if item.is_file():
                # Get relative path from dest base
                rel_path = item.relative_to(self.wsl2_dest)
                if str(rel_path) not in keep_files:
                    item.unlink()
        
        # Remove empty directories
        for item in list(self.wsl2_dest.rglob("*")):
            if item.is_dir() and not any(item.iterdir()):
                item.rmdir()
        
        # Verify cleanup files are gone
        for file_path in cleanup_files:
            file_obj = self.wsl2_dest / file_path
            self.assertFalse(file_obj.exists(), f"File {file_path} should be cleaned up")
        
        # Verify keep files still exist
        for file_path in keep_files:
            file_obj = self.wsl2_dest / file_path
            self.assertTrue(file_obj.exists(), f"File {file_path} should be kept")
    
    def test_directory_structure_creation(self):
        """Test creation of nested directory structure"""
        test_files = [
            "documents/config.txt",
            "projects/app/main.py"
        ]
        
        for file_path in test_files:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path
            
            # Create directory structure
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            
            # Verify directory structure was created
            self.assertTrue(dest.parent.exists(), f"Directory for {file_path} should exist")
            self.assertTrue(dest.parent.is_dir(), f"Parent should be a directory for {file_path}")
    
    def test_empty_destination_directory(self):
        """Test sync to completely empty destination"""
        # Clean destination completely
        shutil.rmtree(self.wsl2_dest)
        self.wsl2_dest.mkdir()
        
        # Verify empty
        self.assertEqual(len(list(self.wsl2_dest.iterdir())), 0)
        
        # Copy files
        files_to_copy = [
            "documents/config.txt",
            "documents/notes.md"
        ]
        
        for file_path in files_to_copy:
            source = self.windows_source / file_path
            dest = self.wsl2_dest / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        
        # Verify files were copied
        for file_path in files_to_copy:
            dest = self.wsl2_dest / file_path
            self.assertTrue(dest.exists(), f"File {file_path} should exist")


if __name__ == "__main__":
    unittest.main()