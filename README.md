# Pics

A command-line tool for organizing photos by separating JPEG and CR3 files into
subdirectories.

## Installation

Install using uv:

```bash
uv tool install pics
```

Or install from source:

```bash
git clone <your-repo>
cd pics
uv tool install .
```

## Usage

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

### Dry Run Mode

Preview what will happen without actually moving files:

```bash
pics organize ./pictures01 --dry-run
pics organize ./pictures01 --prefix vacation --dry-run
```

### Example Output

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

- **Safe operation**: Creates directories as needed and handles errors
  gracefully
- **Case insensitive**: Handles files with different case extensions
- **Intelligent renaming**: Extracts numbers from camera filenames and renames
  sequentially
- **Prefix support**: Add custom prefixes to renamed files (e.g.,
  "vacation-0001.jpg")
- **Dry run mode**: Preview changes before executing
- **Clear feedback**: Shows progress and file counts
- **Error handling**: Continues processing even if individual files fail

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency
management.

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
