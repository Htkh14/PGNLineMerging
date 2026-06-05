# PGN Line Merger

Merges multiple lines in a PGN file into a single game with variations.

## Download

Go to the [Releases page](../../releases/latest) and download the file for your system:

| System | File |
|--------|------|
| Windows | `merge_lines.exe` |
| Linux | `merge_lines` |
| macOS | `merge_lines-mac` |

## Usage

Run the file and a file picker will open. Select your PGN file and it will be merged in place. All lines except the first one will be merged and written into the place of the first one.

You can also pass a file path directly as an argument:
- **Windows:** `merge_lines.exe path\to\file.pgn`
- **Linux/macOS:** `./merge_lines path/to/file.pgn`

## First time setup

**Windows:** SmartScreen may warn the file is unrecognized. Click **More info → Run anyway**. This is normal for unsigned open-source tools.

**Linux:** Make the file executable first:
```bash
chmod +x merge_lines
./merge_lines
```

**macOS:** If blocked by Gatekeeper, go to **System Settings → Privacy & Security** and click **Open Anyway**.