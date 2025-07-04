# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=wslsync

# Run specific test file
pytest tests/test_sync.py
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy wslsync/

# Run all quality checks
black . && isort . && mypy wslsync/
```

### Running the Application
```bash
# Run from source (development)
python -m wslsync

# Run installed version
wslsync

# Common usage patterns
wslsync --dry-run              # Preview changes
wslsync --verbose              # Detailed output
wslsync --validate-config      # Check config validity
wslsync --config /path/to/config  # Use custom config
```

## Project Architecture

WSL Sync is a Python tool that synchronizes files between Windows and WSL2 file systems. The architecture follows a modular design:

### Core Components

- **Configuration (`config.py`)**: Handles parsing and validation of `.wslsync` configuration files. Uses regex to parse simple key-value format with file lists.

- **Sync Engine (`sync.py`)**: Core synchronization logic that copies files from Windows to WSL2 and removes unwanted files. Operates in phases: validate paths → copy files → cleanup destination.

- **Utilities (`utils.py`)**: Helper functions for file operations, logging setup, and common tasks like safe file operations and path validation.

- **CLI Interface (`__main__.py`)**: Command-line interface with argument parsing, supports dry-run mode, verbose logging, and config validation.

### Key Design Patterns

- **Dataclass Configuration**: Uses `@dataclass` for type-safe configuration with `WSLSyncConfig`
- **Path Safety**: Implements path validation to prevent directory traversal attacks
- **Error Handling**: Comprehensive exception handling with descriptive error messages
- **Logging**: Structured logging with configurable levels and optional file output

### File Operations Flow

1. Parse `.wslsync` config file (default: `~/.wslsync`)
2. Validate Windows source and WSL2 destination paths exist
3. Copy specified files and directories from Windows to WSL2:
   - Individual files: Copy with `shutil.copy2` (preserves timestamps)
   - Directories: Copy recursively with `shutil.copytree`
4. Remove files in WSL2 destination that aren't in the sync list or under synced directories
5. Clean up empty directories

### Configuration Format

The `.wslsync` file uses a simple format:
```
windows_base = /mnt/c/MyFiles
wsl2_base = /home/username/sync
files = [
    "documents/config.txt",
    "documents/notes.md",
    "entire_folder",
    "another_directory"
]
```

**Important**: The `files` list can contain both individual files and directories. Directories are copied recursively with all their contents.

### Entry Points

- Console script: `wslsync` command → `wslsync.__main__:main`
- Module execution: `python -m wslsync`

## Development Notes

- Python 3.8+ required
- No external dependencies (uses only stdlib)
- Uses `shutil.copy2` to preserve timestamps
- Implements recursive directory cleanup
- Type hints throughout for better IDE support