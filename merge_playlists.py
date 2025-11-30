import requests
import os
import re

import clean_playlist as cleaner

# Configuration
SETTINGS_FILE = "settings.txt"


def get_category_name(url: str) -> str:
    """
    Extracts the filename from the URL, removes extension, and converts to uppercase.
    Example: https://site.com/fra.m3u -> FRA
    """
    filename = url.split("/")[-1]
    name = os.path.splitext(filename)[0]
    return name.upper()


def process_line(line: str, category_prefix: str) -> str:
    """
    Modifies the #EXTINF line to update the group-title.
    Option B: Prefixes the existing group (e.g., "FRA - News")
    """
    # Regex to find existing group-title
    group_match = re.search(r'group-title="([^"]*)"', line)

    if group_match:
        # If group-title exists, prepend the category prefix
        original_group = group_match.group(1)
        new_group = f"{category_prefix} - {original_group}"
        line = line.replace(
            f'group-title="{original_group}"', f'group-title="{new_group}"'
        )
    else:
        # If no group-title exists, insert it after #EXTINF:-1 or at the start
        # We look for the standard #EXTINF:-1 tag
        if "#EXTINF:-1" in line:
            line = line.replace(
                "#EXTINF:-1", f'#EXTINF:-1 group-title="{category_prefix}"'
            )
        else:
            # Fallback for weird formatting
            line = line.replace(
                "#EXTINF:", f'#EXTINF:0 group-title="{category_prefix}" '
            )

    return line


def merge_playlists() -> None:
    # Check if settings file exists
    if not os.path.exists(SETTINGS_FILE):
        print(f"Error: {SETTINGS_FILE} not found.")
        return

    # Load settings
    settings = cleaner.load_settings(SETTINGS_FILE)
    urls = settings["sources"]
    output_file = settings["output"].get("raw_playlist", "playlist.m3u")
    clean_output = settings["output"].get("clean_playlist", "playlist-clean.m3u")

    if not urls:
        print("Error: No sources found in settings.txt")
        return

    print(f"Found {len(urls)} playlists in {SETTINGS_FILE}...")

    # Open output file and write header
    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write("#EXTM3U\n")

        for url in urls:
            category = get_category_name(url)
            print(f"Processing: {category} ({url})")

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                lines = response.text.splitlines()

                # Logic to parse M3U: preserve EXTINF and URL, ignore file headers
                for i in range(len(lines)):
                    line = lines[i].strip()

                    # We only care about Metadata lines and the URLs immediately following them
                    if line.startswith("#EXTINF"):
                        # Modify the metadata line
                        modified_line = process_line(line, category)

                        # Write metadata line
                        out_f.write(modified_line + "\n")

                        # Look ahead for the URL (usually the next line)
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line and not next_line.startswith("#"):
                                out_f.write(next_line + "\n")

            except Exception as e:
                print(f"Failed to fetch {url}: {e}")

    print(f"\nSuccess! Merged playlist saved to {output_file}")

    # Generate clean playlist
    cleaner.clean_playlist(output_file, clean_output, settings)


if __name__ == "__main__":
    merge_playlists()
