"""
Clean Playlist Module
Transforms raw playlist.m3u into a clean, organized playlist-clean.m3u
"""

import re
from typing import Optional

SETTINGS_FILE = "settings.txt"


def load_settings(filepath: str) -> dict:
    """
    Parses settings.txt and returns a dict with all sections.
    """
    settings = {
        "sources": [],
        "categories_mapping": {},
        "categories_priorities": {},
        "regions": {},
        "output": {},
    }

    current_section = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Check for section header
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].lower().replace(" ", "_")
                continue

            # Parse content based on current section
            if current_section == "sources":
                settings["sources"].append(line)

            elif current_section == "categories_mapping":
                if "=" in line:
                    key, value = line.split("=", 1)
                    settings["categories_mapping"][key.strip()] = value.strip()

            elif current_section == "categories_priorities":
                if "=" in line:
                    key, value = line.split("=", 1)
                    settings["categories_priorities"][key.strip()] = int(value.strip())

            elif current_section == "regions":
                if "=" in line:
                    key, value = line.split("=", 1)
                    settings["regions"][key.strip()] = value.strip()

            elif current_section == "output":
                if "=" in line:
                    key, value = line.split("=", 1)
                    settings["output"][key.strip()] = value.strip()

    return settings


def clean_channel_name(name: str) -> str:
    """
    Cleans channel name by removing resolution tags and availability notes.
    Replaces [Geo-blocked] with globe icon.
    """
    # Check for geo-blocked before removing
    is_geo_blocked = "[Geo-blocked]" in name

    # Remove resolution tags like (480p), (576p), (720p), (1080p), etc.
    name = re.sub(r"\s*\(\d+p\)", "", name)

    # Remove [Not 24/7] and [Geo-blocked]
    name = re.sub(r"\s*\[Not 24/7\]", "", name)
    name = re.sub(r"\s*\[Geo-blocked\]", "", name)

    # Trim whitespace
    name = name.strip()

    # Add globe icon if geo-blocked
    if is_geo_blocked:
        name = f"{name} 🌐"

    return name


def get_clean_region(raw_group: str, regions: dict) -> str:
    """
    Extracts region prefix from group-title and maps to display name.
    Example: "FRA - Animation;Kids" -> "French"
    """
    if " - " in raw_group:
        prefix = raw_group.split(" - ")[0].strip()
        return regions.get(prefix, prefix)
    return "International"


def get_clean_category(
    raw_group: str, mapping: dict, priorities: dict
) -> str:
    """
    Extracts categories from group-title, maps them, and returns the highest priority one.
    Example: "FRA - Animation;Kids" -> "Kids" (because Animation maps to Kids too)
    """
    # Extract category part after " - "
    if " - " in raw_group:
        category_part = raw_group.split(" - ", 1)[1]
    else:
        category_part = raw_group

    # Split by semicolon to get individual categories
    raw_categories = [c.strip() for c in category_part.split(";")]

    # Map each category to its display name
    mapped_categories = []
    for cat in raw_categories:
        mapped = mapping.get(cat, cat)
        if mapped not in mapped_categories:
            mapped_categories.append(mapped)

    # Find the category with highest priority (lowest number)
    best_category = "Autre"
    best_priority = 999

    for cat in mapped_categories:
        priority = priorities.get(cat, 100)
        if priority < best_priority:
            best_priority = priority
            best_category = cat

    return best_category


def parse_extinf_line(line: str) -> Optional[dict]:
    """
    Parses #EXTINF line and extracts metadata.
    Returns dict with tvg_id, tvg_logo, group_title, name, and raw_line.
    """
    if not line.startswith("#EXTINF"):
        return None

    result = {
        "tvg_id": "",
        "tvg_logo": "",
        "group_title": "",
        "name": "",
        "raw_line": line,
    }

    # Extract tvg-id
    tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)
    if tvg_id_match:
        result["tvg_id"] = tvg_id_match.group(1)

    # Extract tvg-logo
    tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line)
    if tvg_logo_match:
        result["tvg_logo"] = tvg_logo_match.group(1)

    # Extract group-title
    group_match = re.search(r'group-title="([^"]*)"', line)
    if group_match:
        result["group_title"] = group_match.group(1)

    # Extract channel name (after the last comma)
    name_match = re.search(r",([^,]+)$", line)
    if name_match:
        result["name"] = name_match.group(1).strip()

    return result


def build_extinf_line(
    tvg_id: str, tvg_logo: str, group_title: str, name: str
) -> str:
    """
    Builds a clean #EXTINF line from components.
    """
    parts = ["#EXTINF:-1"]

    if tvg_id:
        parts.append(f'tvg-id="{tvg_id}"')
    if tvg_logo:
        parts.append(f'tvg-logo="{tvg_logo}"')

    parts.append(f'group-title="{group_title}"')

    return " ".join(parts) + f",{name}"


def clean_playlist(input_file: str, output_file: str, settings: dict) -> None:
    """
    Main function: reads raw playlist, cleans and sorts channels,
    writes to clean playlist file.
    """
    mapping = settings["categories_mapping"]
    priorities = settings["categories_priorities"]
    regions = settings["regions"]

    channels = []

    # Read and parse input file
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF"):
            metadata = parse_extinf_line(line)

            if metadata and i + 1 < len(lines):
                url = lines[i + 1].strip()

                # Skip if URL is empty or another metadata line
                if url and not url.startswith("#"):
                    # Clean the channel data
                    clean_name = clean_channel_name(metadata["name"])
                    clean_region = get_clean_region(
                        metadata["group_title"], regions
                    )
                    clean_category = get_clean_category(
                        metadata["group_title"], mapping, priorities
                    )

                    # Store channel data for sorting
                    channels.append({
                        "region": clean_region,
                        "category": clean_category,
                        "name": clean_name,
                        "tvg_id": metadata["tvg_id"],
                        "tvg_logo": metadata["tvg_logo"],
                        "url": url,
                        "priority": priorities.get(clean_category, 100),
                    })

                    i += 2
                    continue

        i += 1

    # Sort channels: by region (alpha), then category (priority), then name (alpha)
    channels.sort(key=lambda c: (c["region"], c["priority"], c["name"].lower()))

    # Write output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for channel in channels:
            group_title = f"{channel['region']} - {channel['category']}"
            extinf_line = build_extinf_line(
                channel["tvg_id"],
                channel["tvg_logo"],
                group_title,
                channel["name"],
            )
            f.write(extinf_line + "\n")
            f.write(channel["url"] + "\n")

    print(f"Cleaned playlist saved to {output_file}")
    print(f"Total channels: {len(channels)}")
