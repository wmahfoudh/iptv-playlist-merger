# IPTV Playlist Merger

A Python utility that aggregates multiple online IPTV M3U playlists into a single, organized master playlist. It generates both a raw merged playlist (eg. `playlist.m3u`) and a clean, TV-friendly version (eg. `playlist-clean.m3u`) with properly formatted channel names and categories.

## Features

- Merge multiple M3U playlists from URLs
- Automatic category tagging based on source filename
- Clean playlist generation with:
  - Organized categories (News, Kids, Films, etc.)
  - Region-based grouping (Arabic, French, International, etc.)
  - Clean channel names (resolution tags removed)
  - Geo-blocked channels marked with a globe icon
- Fully configurable via a single `settings.txt` file

## Prerequisites

- Python 3.x
- The `requests` library

## Installation

1. Clone this repository or download the files.
2. Install the required Python library:
   ```bash
   pip install requests
   ```

## Configuration

All settings are in `settings.txt`:

### [Sources]
Playlist URLs to merge (one per line):
```
https://iptv-org.github.io/iptv/languages/fra.m3u
https://iptv-org.github.io/iptv/categories/news.m3u
```

### [Categories Mapping]
Map original category names to display names:
```
News=Dépression
Movies=Films
Documentary=Docs
Animation=Kids
```

### [Categories Priorities]
Set display order (lower number = higher priority):
```
Dépression=1
Kids=2
Films=3
Arnaque=22
```

### [Regions]
Map source prefixes to region names:
```
FRA=French
ARA=Arabic
AE=UAE
```

### [Output]
Configure output file names:
```
raw_playlist=playlist.m3u
clean_playlist=playlist-clean.m3u
```

## Usage

1. Edit `settings.txt` to configure your sources and preferences.

2. Run the script:
   ```bash
   python merge_playlists.py
   ```

3. Two files are generated (names configurable in `[Output]` section):
   - `playlist.m3u` - Raw merged playlist with source prefixes
   - `playlist-clean.m3u` - Clean, sorted playlist ready for TV

## Output Example

**Raw playlist (`playlist.m3u`):**
```
#EXTINF:-1 group-title="FRA - Animation;Kids",Disney Jr. (1080p) [Geo-blocked]
```

**Clean playlist (`playlist-clean.m3u`):**
```
#EXTINF:-1 group-title="French - Kids",Disney Jr. 🌐
```

## File Structure

```
iptv-playlist-merger/
├── merge_playlists.py    # Main script
├── clean_playlist.py     # Playlist cleaning module
├── settings.txt          # All configuration
├── playlist.m3u          # Generated raw playlist
└── playlist-clean.m3u    # Generated clean playlist
```

## License

See [LICENSE](LICENSE) file.
