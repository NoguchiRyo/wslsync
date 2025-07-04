"""
Command-line interface for WSL sync tool.

This module provides the main entry point and CLI interface.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .config import parse_config, get_default_config_path, validate_config
from .sync import WSLSyncEngine
from .utils import setup_logging


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="WSL Sync Tool - Synchronize files between Windows and WSL2",
        prog="wslsync"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to .wslsync configuration file"
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration file and exit"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the application.
    
    Args:
        args: Optional list of command-line arguments. If None, uses sys.argv
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        parser = create_argument_parser()
        parsed_args = parser.parse_args(args)
        
        # Handle version command
        if parsed_args.version:
            show_version()
            return 0
        
        # Determine config path
        if parsed_args.config:
            config_path = Path(parsed_args.config)
        else:
            config_path = get_default_config_path()
        
        # Handle validate config command
        if parsed_args.validate_config:
            return validate_config_command(config_path)
        
        # Run sync
        return run_sync(
            config_path=config_path,
            dry_run=parsed_args.dry_run,
            verbose=parsed_args.verbose
        )
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def run_sync(config_path: Path, dry_run: bool = False, verbose: bool = False) -> int:
    """
    Run the synchronization process.
    
    Args:
        config_path: Path to configuration file
        dry_run: If True, show what would be done without actually doing it
        verbose: Enable verbose logging
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Setup logging
        log_level = "DEBUG" if verbose else "INFO"
        logger = setup_logging(log_level=log_level)
        
        # Parse and validate config
        logger.info(f"Loading configuration from: {config_path}")
        config = parse_config(config_path)
        validate_config(config)
        
        # Create sync engine
        engine = WSLSyncEngine(config)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
            
            # Show what would be done
            try:
                source_files = engine.get_source_files()
                dest_files = engine.get_destination_files()
                
                logger.info(f"Would copy {len(source_files)} files")
                for file_path in source_files:
                    logger.info(f"  Would copy: {file_path}")
                
                logger.info(f"Would clean up files not in sync list")
                for file_path in dest_files:
                    rel_path = file_path.relative_to(config.wsl2_base) if config.wsl2_base else file_path
                    # Check if file is under any of the configured paths
                    should_keep = False
                    for config_path in config.files:
                        if str(rel_path) == config_path or str(rel_path).startswith(config_path + "/"):
                            should_keep = True
                            break
                    if not should_keep:
                        logger.info(f"  Would delete: {file_path}")
                        
            except Exception as e:
                logger.error(f"Error during dry run analysis: {e}")
                return 1
        else:
            # Perform actual sync
            logger.info("Starting synchronization")
            engine.sync()
            logger.info("Synchronization completed successfully")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def validate_config_command(config_path: Path) -> int:
    """
    Validate configuration file and report any issues.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Exit code (0 if valid, non-zero if invalid)
    """
    try:
        print(f"Validating configuration file: {config_path}")
        
        # Parse config
        config = parse_config(config_path)
        
        # Validate config
        validate_config(config)
        
        print("✓ Configuration file is valid")
        print(f"  Windows base: {config.windows_base}")
        print(f"  WSL2 base: {config.wsl2_base}")
        print(f"  Files to sync: {len(config.files)}")
        for file_path in config.files:
            print(f"    - {file_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def show_version() -> None:
    """
    Display version information.
    """
    print("wslsync v0.1.0")
    print("A tool for synchronizing files between Windows and WSL2 systems")
    print("Copyright (c) 2025")


if __name__ == "__main__":
    sys.exit(main())