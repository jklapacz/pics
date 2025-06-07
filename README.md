# Pics

A command-line tool for organizing photos by separating JPEG and CR3 files into
subdirectories.

## Installation

Install using uv:

**Organize Command:**

```
pics organize "Week 28" --prefix week28bash
uv tool install pics
```

Or install from source:

```bash
git clone <your-repo>
cd pics
uv tool install .
```

## Usage

### Import Photos from SD Card

```bash
# Import all photos from SD card
pics import /Volumes/SDCardLocation

# Import only weekly photos (Wednesdays) since Nov 6, 2024
pics import /Volumes/SDCardLocation --weekly

# Import and automatically organize with renaming
pics import /Volumes/SDCardLocation --weekly --organize --prefix leon

# Import photos after a specific date
pics import /Volumes/SDCardLocation --after 2025-05-01

# Combine all options
pics import /Volumes/SDCardLocation --weekly --after 2025-05-01 --organize --prefix leon

# Preview what would be imported and organized
pics import /Volumes/SDCardLocation --weekly --organize --prefix leon --dry-run
```

The import command will:

- Scan the source directory recursively for image files
- Filter by date (if `--after` specified)
- Filter to only Wednesdays (if `--weekly` specified)
- Create `Week XX` directories in the current directory
- Copy matching photos to the appropriate week folders
- Optionally organize each week's photos into JPG/RAW subdirectories (if
  `--organize` specified)
- Optionally rename files with week-specific prefixes (if `--prefix` specified)

### Basic Organization

```bash
# Create and populate a photo directory
cd ~/Pictures
mkdir -p pictures01
cp /Volumes/SDCardLocation/.../* ./pictures01/

# Organize the photos
pics organize ./pictures01
```

### With Prefix and Renaming

```bash
# Organize and rename with prefix
pics organize ./pictures01 --prefix vacation

# This will rename files like:
# IMG_8123.jpg -> vacation-0001.jpg
# IMG_8124.jpg -> vacation-0002.jpg
# IMG_8125.CR3 -> vacation-0003.cr3
```

This will:

- Move all JPEG files (`.jpg`, `.jpeg`) to a `JPG/` subdirectory
- Move all CR3 files (`.cr3`) to a `RAW/` subdirectory
- Optionally rename files with a prefix and sequential numbering (starting from
  the lowest camera number)

### Complete Workflow

**Option 1: Import and organize in one step**

```bash
cd ~/Pictures/BabyPhotos
pics import /Volumes/SDCardLocation --weekly --organize --prefix leon
```

**Option 2: Two-step process**

```bash
# 1. Import weekly photos from SD card
cd ~/Pictures/BabyPhotos
pics import /Volumes/SDCardLocation --weekly

# 2. Organize each week's photos
pics organize "Week 28" --prefix "week28"
pics organize "Week 29" --prefix "week29"
```

### Dry Run Mode

Preview what will happen without actually moving files:

```bash
pics import /Volumes/SDCardLocation --weekly --organize --prefix leon --dry-run
pics organize ./pictures01 --dry-run
pics organize ./pictures01 --prefix vacation --dry-run
```

### Example Output

**Import with Auto-organize Command:** **Basic Import Command:**

```
pics import /Volumes/SDCard --weekly --organize --prefix leon

Scanning for image files in /Volumes/SDCard...
Found 245 image files
Weekly mode: Only importing photos from Wednesdays (weekly photo days)
Auto-organize mode: Will organize photos into JPG/RAW subdirectories
Will use prefix 'leon' with week numbers for renaming
After filtering: 12 files in 3 weeks
  Week 28 (2025-05-21): 4 files
  Week 29 (2025-05-28): 4 files
  Week 30 (2025-06-04): 4 files

Created directory: ./Week 28
  Copied: IMG_9123.jpg
  Copied: IMG_9123.CR3
  Copied: IMG_9124.jpg
  Copied: IMG_9124.CR3

Organizing imported photos...

Organizing Week 28...
Found 4 JPEG files and 4 CR3 files
Will rename files with prefix 'leon-week-28' and sequential numbering
Created directory: ./Week 28/JPG
Created directory: ./Week 28/RAW
  Moved and renamed: IMG_9123.jpg -> leon-week-28-0001.jpg
  Moved and renamed: IMG_9124.jpg -> leon-week-28-0002.jpg
  Moved and renamed: IMG_9123.CR3 -> leon-week-28-0001.cr3
  Moved and renamed: IMG_9124.CR3 -> leon-week-28-0002.cr3

Import complete! Photos imported and organized by week in current directory
```

**Basic Import Command:**

```
pics import /Volumes/SDCard --weekly

Scanning for image files in /Volumes/SDCard...
Found 245 image files
Weekly mode: Only importing photos from Wednesdays (weekly photo days)
After filtering: 12 files in 3 weeks
  Week 28 (2025-05-21): 4 files
  Week 29 (2025-05-28): 4 files
  Week 30 (2025-06-04): 4 files

Created directory: ./Week 28
  Copied: IMG_9123.jpg
  Copied: IMG_9123.CR3
  Copied: IMG_9124.jpg
  Copied: IMG_9124.CR3

Created directory: ./Week 29
  Copied: IMG_9125.jpg
  Copied: IMG_9125.CR3
...

Import complete! Photos organized by week in current directory
```

**Organize Command:**

```
Found 50 JPEG files and 50 CR3 files
Will rename files with prefix 'vacation' and sequential numbering
Created directory: /Users/you/Pictures/pictures01/JPG
Created directory: /Users/you/Pictures/pictures01/RAW

Moving 50 JPEG files to JPG/:
  Moved and renamed: IMG_8123.JPEG -> vacation-0001.jpeg
  Moved and renamed: IMG_8124.JPEG -> vacation-0002.jpeg
  ...

Moving 50 CR3 files to RAW/:
  Moved and renamed: IMG_8123.CR3 -> vacation-0001.cr3
  Moved and renamed: IMG_8124.CR3 -> vacation-0002.cr3
  ...

Organization complete! Photos organized in './pictures01'
```

## Features

- **Beautiful progress bars**: Visual feedback with rich progress indicators
- **Weekly photo tracking**: Automatically calculates week numbers since Nov 6,
  2024
- **Smart date filtering**: Import only photos from specific dates or after a
  cutoff
- **Recursive scanning**: Finds images in subdirectories of the source
- **Safe operation**: Creates directories as needed and handles errors
  gracefully
- **Case insensitive**: Handles files with different case extensions
- **Intelligent renaming**: Extracts numbers from camera filenames and renames
  sequentially
- **Prefix support**: Add custom prefixes to renamed files (e.g.,
  "vacation-0001.jpg")
- **Dry run mode**: Preview changes before executing
- **Clear feedback**: Shows progress and file counts with emojis and colors
- **Error handling**: Continues processing even if individual files fail

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency
management.

### Dependencies

- **rich**: Beautiful terminal output with progress bars and colors

### Setup

```bash
# Clone and setup
git clone <your-repo>
cd pics
uv sync

# Run locally
uv run pics organize /path/to/photos

# Install in development mode
uv tool install --editable .
```

## License

MIT License/astral-sh/uv) for dependency management.

```bash
# Clone and setup
git clone <your-repo>
cd pics
uv sync

# Run locally
uv run pics organize /path/to/photos

# Install in development mode
uv tool install --editable .
```

## License

MIT License
