#!/usr/bin/env python3
"""
Photo organization tool for separating JPEG and CR3 files into subdirectories.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

__version__ = "0.1.0"


def extract_number_from_filename(filename: str) -> Optional[int]:
    """
    Extract the numeric part from camera filenames like IMG_1234.jpg or DSC_5678.CR3

    Args:
        filename: The filename to extract number from

    Returns:
        The numeric part as integer, or None if no number found
    """
    # Remove extension and look for numbers
    name_without_ext = Path(filename).stem

    # Try to find numeric patterns - look for sequences of digits
    numbers = re.findall(r"\d+", name_without_ext)

    if numbers:
        # Take the last (usually longest) number found
        # This handles cases like IMG_1234 or DSC05678 or even complex names
        return int(numbers[-1])

    return None


def create_filename_mapping(
    files: List[Path], prefix: Optional[str] = None
) -> Dict[Path, str]:
    """
    Create a mapping from original files to new filenames with sequential numbering.

    Args:
        files: List of file paths to rename
        prefix: Optional prefix for new filenames

    Returns:
        Dictionary mapping original path to new filename
    """
    if not files:
        return {}

    # Extract numbers and sort files by their numeric part
    file_numbers = []
    for file_path in files:
        number = extract_number_from_filename(file_path.name)
        file_numbers.append((file_path, number if number is not None else float("inf")))

    # Sort by the extracted number (files without numbers go to the end)
    file_numbers.sort(key=lambda x: x[1])

    # Create mapping with sequential numbering
    mapping = {}
    for i, (file_path, _) in enumerate(file_numbers, 1):
        if prefix:
            new_name = f"{prefix}-{i:04d}{file_path.suffix.lower()}"
        else:
            new_name = file_path.name
        mapping[file_path] = new_name

    return mapping


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


def organize_photos(
    target_directory: str, prefix: Optional[str] = None, dry_run: bool = False
) -> None:
    """
    Organize photos in the target directory by moving JPEGs to JPG/ and CR3s to RAW/.
    Optionally rename files with a prefix and sequential numbering.

    Args:
        target_directory: Directory containing the photos to organize
        prefix: Optional prefix for renaming files (e.g., "vacation" -> "vacation-0001.jpg")
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

    # Create filename mappings for renaming
    jpeg_mapping = create_filename_mapping(jpeg_files, prefix)
    cr3_mapping = create_filename_mapping(cr3_files, prefix)

    if prefix:
        print(f"Will rename files with prefix '{prefix}' and sequential numbering")

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
        for jpeg_file in sorted(
            jpeg_files, key=lambda f: extract_number_from_filename(f.name) or 0
        ):
            new_filename = jpeg_mapping[jpeg_file]
            destination = jpg_dir / new_filename
            if dry_run:
                print(f"  Would move: {jpeg_file.name} -> JPG/{new_filename}")
            else:
                try:
                    shutil.move(str(jpeg_file), str(destination))
                    if prefix:
                        print(
                            f"  Moved and renamed: {jpeg_file.name} -> {new_filename}"
                        )
                    else:
                        print(f"  Moved: {jpeg_file.name}")
                except Exception as e:
                    print(f"  Error moving {jpeg_file.name}: {e}")

    # Move CR3 files
    if cr3_files:
        print(f"\nMoving {len(cr3_files)} CR3 files to RAW/:")
        for cr3_file in sorted(
            cr3_files, key=lambda f: extract_number_from_filename(f.name) or 0
        ):
            new_filename = cr3_mapping[cr3_file]
            destination = raw_dir / new_filename
            if dry_run:
                print(f"  Would move: {cr3_file.name} -> RAW/{new_filename}")
            else:
                try:
                    shutil.move(str(cr3_file), str(destination))
                    if prefix:
                        print(f"  Moved and renamed: {cr3_file.name} -> {new_filename}")
                    else:
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
        "--prefix",
        help="Prefix for renaming files (e.g., 'vacation' -> 'vacation-0001.jpg')",
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
        organize_photos(args.directory, prefix=args.prefix, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
