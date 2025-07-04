# WSL Sync Tool

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

A powerful and flexible tool for synchronizing files and directories between Windows and WSL2 systems. WSL Sync provides seamless bidirectional file synchronization with support for both individual files and entire directory trees.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

WSL Sync bridges the gap between Windows and WSL2 file systems, enabling efficient synchronization of files and directories. Whether you're working with individual configuration files or entire project directories, WSL Sync provides a reliable and configurable solution.

### Key Benefits

- **Flexible Synchronization**: Sync individual files or entire directory trees
- **Intelligent Cleanup**: Automatically removes files not in the sync list
- **Safe Operations**: Built-in path validation and error handling
- **Configuration-Driven**: Simple text-based configuration
- **Dry-Run Support**: Preview changes before applying them
- **Logging**: Comprehensive logging with configurable verbosity

## Features

### ✅ Core Features

- **Mixed File/Directory Sync**: Configure both individual files and directories in a single operation
- **Recursive Directory Copying**: Automatically handles nested directory structures
- **Timestamp Preservation**: Maintains file modification times during sync
- **Intelligent Cleanup**: Removes outdated files while preserving synced content
- **Safe Path Handling**: Prevents directory traversal attacks
- **Cross-Platform Paths**: Handles Windows and Linux path formats seamlessly

### 🔧 Operation Modes

- **Standard Sync**: Full synchronization with copy and cleanup
- **Dry Run**: Preview mode to see what changes would be made
- **Validation**: Configuration file validation and verification
- **Verbose Logging**: Detailed operation logging for debugging

### 🛡️ Safety Features

- **Path Validation**: Ensures all paths are safe and within configured boundaries
- **Error Handling**: Comprehensive error reporting with actionable messages
- **Backup Safety**: Won't overwrite unless explicitly configured
- **Permission Checks**: Validates read/write permissions before operations

## Installation

### Prerequisites

- Python 3.8 or higher
- WSL2 environment
- Access to both Windows and WSL2 file systems

### Install from Source

```bash
# Clone the repository
git clone https://github.com/example/wslsync.git
cd wslsync

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Install with Development Dependencies

```bash
# Install with development tools
pip install -e ".[dev]"

# This includes: pytest, black, isort, mypy
```

### Install from PyPI (Coming Soon)

```bash
pip install wslsync
```

## Quick Start

### 1. Create Configuration File

Create a `.wslsync` file in your home directory:

```bash
# Create config file
touch ~/.wslsync
```

### 2. Configure Sync Paths

Edit `~/.wslsync`:

```ini
# WSL Sync Configuration
windows_base = /mnt/c/Users/YourName/Documents
wsl2_base = /home/username/sync
files = [
    "config.txt",
    "projects/myapp",
    "scripts"
]
```

### 3. Run Sync

```bash
# Preview changes (dry run)
wslsync --dry-run

# Perform sync
wslsync

# Sync with verbose output
wslsync --verbose
```

## Configuration

### Configuration File Format

The `.wslsync` configuration file uses a simple key-value format:

```ini
# Base directory on Windows (mounted in WSL2)
windows_base = /mnt/c/path/to/windows/directory

# Base directory in WSL2 where files will be synced
wsl2_base = /home/username/sync

# List of files and directories to sync (relative to windows_base)
files = [
    "file1.txt",
    "directory1",
    "subdirectory/file2.txt",
    "entire_project_folder"
]
```

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `windows_base` | Path | Yes | Source directory on Windows (WSL2 mount point) |
| `wsl2_base` | Path | Yes | Destination directory in WSL2 |
| `files` | List | Yes | Files and directories to synchronize |

### Default Configuration Location

- **Default**: `~/.wslsync` (user home directory)
- **Custom**: Specify with `--config /path/to/config`

## Usage

### Command Line Interface

```bash
wslsync [OPTIONS]
```

### Available Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config PATH` | `-c` | Path to configuration file |
| `--dry-run` | `-n` | Preview changes without applying |
| `--verbose` | `-v` | Enable verbose output |
| `--validate-config` | | Validate configuration file |
| `--version` | | Show version information |
| `--help` | `-h` | Show help message |

### Common Usage Patterns

```bash
# Basic sync with default config
wslsync

# Sync with custom configuration
wslsync --config /path/to/custom/.wslsync

# Preview changes before sync
wslsync --dry-run

# Verbose sync for debugging
wslsync --verbose

# Validate configuration
wslsync --validate-config

# Combine options
wslsync --config /path/to/config --dry-run --verbose
```

## Examples

### Example 1: Basic File Sync

**Configuration** (`~/.wslsync`):
```ini
windows_base = /mnt/c/Users/John/Documents
wsl2_base = /home/john/sync
files = [
    "config.txt",
    "notes.md",
    "backup.sh"
]
```

**Usage**:
```bash
# Sync files
wslsync

# Output:
# INFO - Loading configuration from: /home/john/.wslsync
# INFO - Starting synchronization
# INFO - Synchronization completed successfully
```

### Example 2: Project Directory Sync

**Configuration**:
```ini
windows_base = /mnt/c/Development
wsl2_base = /home/developer/projects
files = [
    "myapp",
    "shared-libs",
    "config/production.json"
]
```

**Directory Structure**:
```
/mnt/c/Development/
├── myapp/
│   ├── src/
│   │   ├── main.py
│   │   └── utils.py
│   ├── tests/
│   │   └── test_main.py
│   └── requirements.txt
├── shared-libs/
│   └── common.py
└── config/
    └── production.json
```

**Result in WSL2**:
```
/home/developer/projects/
├── myapp/
│   ├── src/
│   │   ├── main.py
│   │   └── utils.py
│   ├── tests/
│   │   └── test_main.py
│   └── requirements.txt
├── shared-libs/
│   └── common.py
└── config/
    └── production.json
```

### Example 3: Mixed Content Sync

**Configuration**:
```ini
windows_base = /mnt/c/Users/Alice/Work
wsl2_base = /home/alice/workspace
files = [
    "current-project",
    "templates/base.html",
    "scripts/deploy.sh",
    "docs",
    "config.json"
]
```

### Example 4: Dry Run Example

```bash
$ wslsync --dry-run

INFO - Loading configuration from: /home/user/.wslsync
INFO - DRY RUN MODE - No changes will be made
INFO - Would copy 15 files
INFO -   Would copy: /mnt/c/Users/User/Documents/project/main.py
INFO -   Would copy: /mnt/c/Users/User/Documents/project/utils.py
INFO -   Would copy: /mnt/c/Users/User/Documents/config.json
INFO - Would clean up files not in sync list
INFO -   Would delete: /home/user/sync/old_file.txt
```

### Example 5: Verbose Output

```bash
$ wslsync --verbose

DEBUG - Validating configuration settings
DEBUG - Windows base path: /mnt/c/Users/User/Documents
DEBUG - WSL2 base path: /home/user/sync
DEBUG - Files to sync: ['project', 'config.json']
INFO - Loading configuration from: /home/user/.wslsync
DEBUG - Validating source and destination paths
DEBUG - Copying file: /mnt/c/Users/User/Documents/config.json
DEBUG - Copying directory: /mnt/c/Users/User/Documents/project
DEBUG - Created directory: /home/user/sync/project
DEBUG - Copied file: /home/user/sync/project/main.py
DEBUG - Copied file: /home/user/sync/project/utils.py
INFO - Starting synchronization
DEBUG - Cleanup: preserving 3 files
DEBUG - Cleanup: removed 1 obsolete file
INFO - Synchronization completed successfully
```

## API Reference

### Configuration Classes

#### `WSLSyncConfig`

```python
@dataclass
class WSLSyncConfig:
    """Configuration for WSL sync operations."""
    windows_base: Optional[Path] = None
    wsl2_base: Optional[Path] = None
    files: List[str] = field(default_factory=list)
```

#### Configuration Functions

```python
def parse_config(config_path: Path) -> WSLSyncConfig:
    """Parse configuration file and return WSLSyncConfig object."""

def validate_config(config: WSLSyncConfig) -> bool:
    """Validate configuration settings."""

def get_default_config_path() -> Path:
    """Get default configuration file path."""
```

### Sync Engine

#### `WSLSyncEngine`

```python
class WSLSyncEngine:
    """Main synchronization engine."""
    
    def __init__(self, config: WSLSyncConfig) -> None:
        """Initialize with configuration."""
    
    def sync(self) -> None:
        """Perform complete synchronization."""
    
    def copy_files(self) -> List[Path]:
        """Copy files and directories from source to destination."""
    
    def cleanup_destination(self, keep_files: Set[Path]) -> List[Path]:
        """Remove files not in sync list."""
    
    def validate_paths(self) -> bool:
        """Validate source and destination paths."""
```

### Utility Functions

```python
def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> logging.Logger:
    """Set up logging configuration."""

def safe_copy_file(source: Path, destination: Path, preserve_timestamps: bool = True) -> bool:
    """Safely copy a file with error handling."""

def is_path_safe(path: Path, base_path: Path) -> bool:
    """Check if path is safe (within base directory)."""
```

## Advanced Usage

### Programmatic Usage

```python
from pathlib import Path
from wslsync.config import WSLSyncConfig, parse_config
from wslsync.sync import WSLSyncEngine

# Create config programmatically
config = WSLSyncConfig(
    windows_base=Path("/mnt/c/Users/User/Documents"),
    wsl2_base=Path("/home/user/sync"),
    files=["project1", "config.json", "scripts"]
)

# Or load from file
config = parse_config(Path("~/.wslsync"))

# Create and run sync engine
engine = WSLSyncEngine(config)
engine.sync()
```

### Custom Logging

```python
from wslsync.utils import setup_logging
from pathlib import Path

# Set up custom logging
logger = setup_logging(
    log_level="DEBUG",
    log_file=Path("/var/log/wslsync.log")
)

# Use logger
logger.info("Custom sync operation starting")
```

### Error Handling

```python
from wslsync.sync import WSLSyncEngine
from wslsync.config import parse_config

try:
    config = parse_config(Path("~/.wslsync"))
    engine = WSLSyncEngine(config)
    engine.sync()
except FileNotFoundError as e:
    print(f"File not found: {e}")
except PermissionError as e:
    print(f"Permission denied: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Troubleshooting

### Common Issues

#### Configuration File Not Found

**Error**: `FileNotFoundError: Config file not found`

**Solution**:
```bash
# Create config file
touch ~/.wslsync

# Or specify custom location
wslsync --config /path/to/config
```

#### Permission Denied

**Error**: `PermissionError: Permission denied`

**Solutions**:
- Check file permissions: `ls -la /path/to/file`
- Ensure WSL2 has access to Windows directories
- Run with appropriate permissions

#### Path Not Found

**Error**: `FileNotFoundError: Source directory not found`

**Solutions**:
- Verify Windows path is correctly mounted in WSL2
- Check path exists: `ls /mnt/c/path/to/directory`
- Ensure correct path format in configuration

#### Invalid Configuration

**Error**: `ValueError: Configuration error`

**Solutions**:
```bash
# Validate configuration
wslsync --validate-config

# Check configuration format
cat ~/.wslsync
```

### Debugging

#### Enable Verbose Logging

```bash
# Verbose output
wslsync --verbose

# Dry run with verbose output
wslsync --dry-run --verbose
```

#### Check Configuration

```bash
# Validate configuration
wslsync --validate-config

# Output:
# Validating configuration file: /home/user/.wslsync
# ✓ Configuration file is valid
#   Windows base: /mnt/c/Users/User/Documents
#   WSL2 base: /home/user/sync
#   Files to sync: 3
#     - project
#     - config.json
#     - scripts
```

### Performance Considerations

- **Large Directories**: Consider breaking large directories into smaller chunks
- **Network Drives**: Be aware of potential latency with network-mounted drives
- **Frequent Sync**: Use dry-run mode to preview changes before frequent syncs

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wslsync

# Run specific test file
pytest tests/test_sync.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy wslsync/

# Run all checks
black . && isort . && mypy wslsync/
```

### Project Structure

```
wslsync/
├── wslsync/
│   ├── __init__.py
│   ├── __main__.py      # CLI interface
│   ├── config.py        # Configuration handling
│   ├── sync.py          # Core sync engine
│   └── utils.py         # Utility functions
├── tests/
│   ├── test_config.py
│   ├── test_sync.py
│   ├── test_main.py
│   └── test_utils.py
├── README.md
├── CLAUDE.md
├── pyproject.toml
└── LICENSE
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone repository
git clone https://github.com/example/wslsync.git
cd wslsync

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black . && isort .
```

### Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for changes
- Use type hints throughout code

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/example/wslsync/issues)
- **Documentation**: Additional documentation available in [CLAUDE.md](CLAUDE.md)
- **Contributing**: See [Contributing](#contributing) section above

---

**WSL Sync Tool** - Bridging Windows and WSL2 file systems seamlessly.