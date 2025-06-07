#!/usr/bin/env python3
"""
Photo organization tool for separating JPEG and CR3 files into subdirectories.
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

__version__ = "0.1.0"


def find_photo_files(directory: Path) -> Tuple[List[Path], List[Path]]:
    """
    Find all JPEG and CR3 files in the given directory.

    Args:
        directory: Path to search for photo files

    Returns:
        Tuple of (jpeg_files, cr3_files) lists
    """
    jpeg_files = []
    cr3_files = []

    # Look for files with these extensions (case insensitive)
    jpeg_extensions = {".jpg", ".jpeg"}
    cr3_extensions = {".cr3"}

    for file_path in directory.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in jpeg_extensions:
                jpeg_files.append(file_path)
            elif ext in cr3_extensions:
                cr3_files.append(file_path)

    return jpeg_files, cr3_files


def organize_photos(target_directory: str, dry_run: bool = False) -> None:
    """
    Organize photos in the target directory by moving JPEGs to JPG/ and CR3s to RAW/.

    Args:
        target_directory: Directory containing the photos to organize
        dry_run: If True, only show what would be done without actually moving files
    """
    target_path = Path(target_directory).resolve()

    if not target_path.exists():
        print(f"Error: Directory '{target_directory}' does not exist")
        sys.exit(1)

    if not target_path.is_dir():
        print(f"Error: '{target_directory}' is not a directory")
        sys.exit(1)

    # Find all photo files
    jpeg_files, cr3_files = find_photo_files(target_path)

    if not jpeg_files and not cr3_files:
        print(f"No JPEG or CR3 files found in '{target_directory}'")
        return

    print(f"Found {len(jpeg_files)} JPEG files and {len(cr3_files)} CR3 files")

    # Create subdirectories
    jpg_dir = target_path / "JPG"
    raw_dir = target_path / "RAW"

    if dry_run:
        print("\nDRY RUN - Would perform these actions:")
        if jpeg_files:
            print(f"Would create directory: {jpg_dir}")
        if cr3_files:
            print(f"Would create directory: {raw_dir}")
    else:
        if jpeg_files:
            jpg_dir.mkdir(exist_ok=True)
            print(f"Created directory: {jpg_dir}")
        if cr3_files:
            raw_dir.mkdir(exist_ok=True)
            print(f"Created directory: {raw_dir}")

    # Move JPEG files
    if jpeg_files:
        print(f"\nMoving {len(jpeg_files)} JPEG files to JPG/:")
        for jpeg_file in sorted(jpeg_files):
            destination = jpg_dir / jpeg_file.name
            if dry_run:
                print(f"  Would move: {jpeg_file.name} -> JPG/{jpeg_file.name}")
            else:
                try:
                    shutil.move(str(jpeg_file), str(destination))
                    print(f"  Moved: {jpeg_file.name}")
                except Exception as e:
                    print(f"  Error moving {jpeg_file.name}: {e}")

    # Move CR3 files
    if cr3_files:
        print(f"\nMoving {len(cr3_files)} CR3 files to RAW/:")
        for cr3_file in sorted(cr3_files):
            destination = raw_dir / cr3_file.name
            if dry_run:
                print(f"  Would move: {cr3_file.name} -> RAW/{cr3_file.name}")
            else:
                try:
                    shutil.move(str(cr3_file), str(destination))
                    print(f"  Moved: {cr3_file.name}")
                except Exception as e:
                    print(f"  Error moving {cr3_file.name}: {e}")

    if not dry_run:
        print(f"\nOrganization complete! Photos organized in '{target_directory}'")


def main():
    """Main entry point for the pics command-line tool."""
    parser = argparse.ArgumentParser(
        description="Organize photos by separating JPEG and CR3 files into subdirectories",
        prog="pics",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Organize command
    organize_parser = subparsers.add_parser(
        "organize", help="Organize photos in a directory"
    )
    organize_parser.add_argument(
        "directory", help="Directory containing photos to organize"
    )
    organize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving files",
    )

    # Version command
    parser.add_argument("--version", action="version", version=f"pics {__version__}")

    # Parse arguments
    args = parser.parse_args()

    if args.command == "organize":
        organize_photos(args.directory, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
