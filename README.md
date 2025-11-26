# IPTV Playlist Merger

This project contains a Python script that aggregates multiple online IPTV M3U playlists into a single, organized master playlist (`playlist.m3u`).

## How it Works

The script reads a list of M3U URLs from a text file, downloads them, and merges them. To keep things organized, it uses the filename of the source URL to tag the channels.

**Example Logic:**
1. **Source:** `https://example.com/fra.m3u`
2. **Category Name:** Derived from filename -> `FRA`
3. **Channel Update:** 
   *   Original: `group-title="News"`
   *   Result: `group-title="FRA - News"`

## Prerequisites

*   Python 3.x
*   The `requests` library

## Installation

1.  Clone this repository or download the files.
2.  Install the required Python library:
    ```bash
    pip install requests
    ```

## Usage

1.  **Edit Sources:**
    Open `sources.txt` and add the links to the M3U playlists you want to merge (one URL per line).
    
    *Example `sources.txt`:*
    ```text
    https://iptv-org.github.io/iptv/languages/fra.m3u
    https://iptv-org.github.io/iptv/languages/deu.m3u
    https://iptv-org.github.io/iptv/categories/sports.m3u
    ```

2.  **Run the Script:**
    Execute the Python script:
    ```bash
    python merge_playlists.py
    ```

3.  **Get Result:**
    The script will generate a new file named `playlist.m3u` in the same directory. You can now load this file into your IPTV player or set up a hotlink to it.
