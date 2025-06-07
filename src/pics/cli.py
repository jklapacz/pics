#!/usr/bin/env python3
"""
Photo organization tool for separating JPEG and CR3 files into subdirectories.
"""

import argparse
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

__version__ = "0.1.0"

# Weekly photo schedule - starting Wed Nov 13, 2024
WEEKLY_START_DATE = datetime(2024, 11, 13)  # Wednesday, November 13, 2024

# Initialize rich console
console = Console()


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


def get_file_date(file_path: Path) -> Optional[datetime]:
    """
    Get the creation/modification date of a file.

    Args:
        file_path: Path to the file

    Returns:
        DateTime object or None if unable to determine
    """
    try:
        # Try to get creation time first, fall back to modification time
        stat = file_path.stat()
        # Use the earlier of creation time or modification time
        timestamp = min(stat.st_ctime, stat.st_mtime)
        return datetime.fromtimestamp(timestamp)
    except Exception:
        return None


def calculate_week_number(date: datetime) -> int:
    """
    Calculate the week number since the start of weekly photos.

    Args:
        date: The date to calculate week for

    Returns:
        Week number (1-based)
    """
    # Calculate days since start
    days_since_start = (date.date() - WEEKLY_START_DATE.date()).days

    # Calculate week number (1-based)
    week_number = (days_since_start // 7) + 1

    return max(1, week_number)


def is_weekly_photo_day(date: datetime) -> bool:
    """
    Check if the given date is a weekly photo day (Wednesday).

    Args:
        date: Date to check

    Returns:
        True if it's a Wednesday (weekly photo day)
    """
    return date.weekday() == 2  # Wednesday = 2


def find_all_image_files(directory: Path) -> List[Path]:
    """
    Recursively find all image files in a directory with progress indication.

    Args:
        directory: Directory to search

    Returns:
        List of image file paths
    """
    image_files = []
    image_extensions = {".jpg", ".jpeg", ".cr3", ".raw", ".png", ".tiff", ".tif"}

    console.print(f"🔍 Scanning for image files in {directory}...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        scan_task = progress.add_task("Scanning directories...", total=None)

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)
                progress.update(
                    scan_task, description=f"Found {len(image_files)} images..."
                )

    return image_files


def import_photos(
    source_directory: str,
    weekly: bool = False,
    after_date: Optional[str] = None,
    organize: bool = False,
    prefix: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    Import photos from an SD card or source directory.

    Args:
        source_directory: Path to source directory (e.g., SD card)
        weekly: If True, only import photos from weekly photo days (Wednesdays)
        after_date: Only import photos after this date (YYYY-MM-DD format)
        organize: If True, automatically organize each week's photos into JPG/RAW subdirectories
        prefix: Prefix for renaming files when organizing (e.g., "leon" -> "leon-week-29-0001.jpg")
        dry_run: If True, show what would be done without actually copying files
    """
    source_path = Path(source_directory).resolve()

    if not source_path.exists():
        print(f"Error: Source directory '{source_directory}' does not exist")
        sys.exit(1)

    if not source_path.is_dir():
        print(f"Error: '{source_directory}' is not a directory")
        sys.exit(1)

    # Parse after_date if provided
    after_datetime = None
    if after_date:
        try:
            after_datetime = datetime.strptime(after_date, "%Y-%m-%d")
            print(f"Only importing photos after {after_date}")
        except ValueError:
            print(f"Error: Invalid date format '{after_date}'. Use YYYY-MM-DD format.")
            sys.exit(1)

    if weekly:
        print("Weekly mode: Only importing photos from Wednesdays (weekly photo days)")

    if organize:
        print("Auto-organize mode: Will organize photos into JPG/RAW subdirectories")
        if prefix:
            print(f"Will use prefix '{prefix}' with week numbers for renaming")

    # Find all image files
    print(f"Scanning for image files in {source_directory}...")
    image_files = find_all_image_files(source_path)

    if not image_files:
        console.print("❌ No image files found in source directory")
        return

    console.print(f"✅ Found {len(image_files)} image files")

    # Group files by week with progress
    weekly_groups: Dict[int, List[Path]] = {}
    filtered_files = []

    console.print("🔄 Processing and filtering files...")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        filter_task = progress.add_task("Filtering files...", total=len(image_files))

        for file_path in image_files:
            file_date = get_file_date(file_path)

            if not file_date:
                console.print(
                    f"⚠️  Warning: Could not determine date for {file_path.name}, skipping"
                )
                progress.advance(filter_task)
                continue

            # Apply after_date filter
            if after_datetime and file_date < after_datetime:
                progress.advance(filter_task)
                continue

            # Apply weekly filter
            if weekly and not is_weekly_photo_day(file_date):
                progress.advance(filter_task)
                continue

            filtered_files.append(file_path)
            week_number = calculate_week_number(file_date)

            if week_number not in weekly_groups:
                weekly_groups[week_number] = []
            weekly_groups[week_number].append(file_path)

            progress.advance(filter_task)

    if not filtered_files:
        if weekly:
            console.print("❌ No photos found from weekly photo days (Wednesdays)")
        elif after_datetime:
            console.print(f"❌ No photos found after {after_date}")
        else:
            console.print("❌ No photos found matching criteria")
        return

    console.print(
        f"✅ After filtering: {len(filtered_files)} files in {len(weekly_groups)} weeks"
    )

    # Show what weeks we found
    for week_num in sorted(weekly_groups.keys()):
        files_count = len(weekly_groups[week_num])
        # Calculate the actual date of this week
        week_date = WEEKLY_START_DATE + timedelta(weeks=week_num - 1)
        console.print(
            f"  📅 Week {week_num} ({week_date.strftime('%Y-%m-%d')}): {files_count} files"
        )

    if dry_run:
        current_dir = Path.cwd()
        console.print("\n🔍 DRY RUN - Would create these directories and copy files:")
        # Show dry run details without progress bars
        for week_num in sorted(weekly_groups.keys()):
            week_dir = current_dir / f"Week {week_num:02d}"
            console.print(f"Would create directory: {week_dir}")
            for file_path in weekly_groups[week_num]:
                console.print(f"  Would copy: {file_path.name}")
        return

    # Create week directories and copy files with progress
    current_dir = Path.cwd()
    created_week_dirs = []

    console.print("\n📂 Copying files to week directories...")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        copy_task = progress.add_task("Copying files...", total=len(filtered_files))

        for week_num in sorted(weekly_groups.keys()):
            week_dir = current_dir / f"Week {week_num:02d}"
            week_dir.mkdir(exist_ok=True)
            created_week_dirs.append(week_dir)

            progress.update(copy_task, description=f"Copying to Week {week_num:02d}...")

            for file_path in weekly_groups[week_num]:
                destination = week_dir / file_path.name

                try:
                    shutil.copy2(str(file_path), str(destination))
                    progress.advance(copy_task)
                except Exception as e:
                    console.print(f"❌ Error copying {file_path.name}: {e}")
                    progress.advance(copy_task)

    # If organize flag is set, organize each week directory
    if organize:
        console.print("\n📁 Organizing imported photos...")

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            organize_task = progress.add_task(
                "Organizing weeks...", total=len(created_week_dirs)
            )

            for week_dir in created_week_dirs:
                week_num = int(week_dir.name.split()[-1])  # Extract week number

                # Create week-specific prefix if base prefix provided
                if prefix:
                    week_prefix = f"{prefix}-week-{week_num:02d}"
                else:
                    week_prefix = None

                progress.update(
                    organize_task, description=f"Organizing {week_dir.name}..."
                )
                organize_photos(str(week_dir), prefix=week_prefix, dry_run=False)
                progress.advance(organize_task)

    elif organize and dry_run:
        console.print("\n🔍 Would organize each week directory:")
        for week_num in sorted(weekly_groups.keys()):
            week_dir = current_dir / f"Week {week_num:02d}"
            if prefix:
                week_prefix = f"{prefix}-week-{week_num:02d}"
                console.print(
                    f"  Would organize {week_dir.name} with prefix '{week_prefix}'"
                )
            else:
                console.print(f"  Would organize {week_dir.name}")

    action = "imported and organized" if organize else "imported"
    console.print(f"\n🎉 Import complete! Photos {action} by week in current directory")


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
        console.print(f"❌ Error: Directory '{target_directory}' does not exist")
        sys.exit(1)

    if not target_path.is_dir():
        console.print(f"❌ Error: '{target_directory}' is not a directory")
        sys.exit(1)

    # Find all photo files
    jpeg_files, cr3_files = find_photo_files(target_path)

    if not jpeg_files and not cr3_files:
        console.print(f"❌ No JPEG or CR3 files found in '{target_directory}'")
        return

    console.print(
        f"✅ Found {len(jpeg_files)} JPEG files and {len(cr3_files)} CR3 files"
    )

    # Create filename mappings for renaming
    jpeg_mapping = create_filename_mapping(jpeg_files, prefix)
    cr3_mapping = create_filename_mapping(cr3_files, prefix)

    if prefix:
        console.print(
            f"🏷️  Will rename files with prefix '{prefix}' and sequential numbering"
        )

    # Create subdirectories
    jpg_dir = target_path / "JPG"
    raw_dir = target_path / "RAW"

    if dry_run:
        console.print("\n🔍 DRY RUN - Would perform these actions:")
        if jpeg_files:
            console.print(f"Would create directory: {jpg_dir}")
        if cr3_files:
            console.print(f"Would create directory: {raw_dir}")

        # Show what files would be moved
        if jpeg_files:
            console.print(f"\nWould move {len(jpeg_files)} JPEG files to JPG/:")
            for jpeg_file in sorted(
                jpeg_files, key=lambda f: extract_number_from_filename(f.name) or 0
            ):
                new_filename = jpeg_mapping[jpeg_file]
                console.print(f"  Would move: {jpeg_file.name} -> JPG/{new_filename}")

        if cr3_files:
            console.print(f"\nWould move {len(cr3_files)} CR3 files to RAW/:")
            for cr3_file in sorted(
                cr3_files, key=lambda f: extract_number_from_filename(f.name) or 0
            ):
                new_filename = cr3_mapping[cr3_file]
                console.print(f"  Would move: {cr3_file.name} -> RAW/{new_filename}")
        return

    # Create directories
    if jpeg_files:
        jpg_dir.mkdir(exist_ok=True)
        console.print(f"📁 Created directory: {jpg_dir}")
    if cr3_files:
        raw_dir.mkdir(exist_ok=True)
        console.print(f"📁 Created directory: {raw_dir}")

    total_files = len(jpeg_files) + len(cr3_files)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        move_task = progress.add_task(
            "Moving and organizing files...", total=total_files
        )

        # Move JPEG files
        if jpeg_files:
            for jpeg_file in sorted(
                jpeg_files, key=lambda f: extract_number_from_filename(f.name) or 0
            ):
                new_filename = jpeg_mapping[jpeg_file]
                destination = jpg_dir / new_filename
                try:
                    shutil.move(str(jpeg_file), str(destination))
                    progress.advance(move_task)
                except Exception as e:
                    console.print(f"❌ Error moving {jpeg_file.name}: {e}")
                    progress.advance(move_task)

        # Move CR3 files
        if cr3_files:
            for cr3_file in sorted(
                cr3_files, key=lambda f: extract_number_from_filename(f.name) or 0
            ):
                new_filename = cr3_mapping[cr3_file]
                destination = raw_dir / new_filename
                try:
                    shutil.move(str(cr3_file), str(destination))
                    progress.advance(move_task)
                except Exception as e:
                    console.print(f"❌ Error moving {cr3_file.name}: {e}")
                    progress.advance(move_task)

    console.print(
        f"\n🎉 Organization complete! Photos organized in '{target_directory}'"
    )


def main():
    """Main entry point for the pics command-line tool."""
    parser = argparse.ArgumentParser(
        description="Organize photos by separating JPEG and CR3 files into subdirectories",
        prog="pics",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import command
    import_parser = subparsers.add_parser(
        "import", help="Import photos from SD card or source directory"
    )
    import_parser.add_argument("source", help="Source directory (e.g., SD card path)")
    import_parser.add_argument(
        "--weekly",
        action="store_true",
        help="Only import photos from weekly photo days (Wednesdays)",
    )
    import_parser.add_argument(
        "--after", help="Only import photos after this date (YYYY-MM-DD format)"
    )
    import_parser.add_argument(
        "--organize",
        action="store_true",
        help="Automatically organize imported photos into JPG/RAW subdirectories",
    )
    import_parser.add_argument(
        "--prefix",
        help="Prefix for renaming files when organizing (e.g., 'leon' -> 'leon-week-29-0001.jpg')",
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually copying files",
    )

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

    if args.command == "import":
        import_photos(
            args.source,
            weekly=args.weekly,
            after_date=args.after,
            organize=args.organize,
            prefix=args.prefix,
            dry_run=args.dry_run,
        )
    elif args.command == "organize":
        organize_photos(args.directory, prefix=args.prefix, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
