"""Map loading and discovery utilities."""

from pathlib import Path
from ..cls_data import Data
from ..parser.file_parse import parse_file, parse_text


def load_map_from_file(file_path: str) -> Data | None:
    """Load a map file and return a Data object."""
    try:
        with open(file_path, "r") as file:
            data = parse_text(parse_file(file))
        return data
    except Exception as e:
        print(f"Error loading map '{file_path}': {e}")
        return None


def get_available_maps() -> dict[str, list[tuple[str, str]]]:
    """Get available maps organized by category.

    Returns a dict where keys are category names
    and values are lists of (map_name, file_path) tuples.
    """
    maps_folder = Path("maps")
    available_maps: dict[str, list[tuple[str, str]]] = {}

    if not maps_folder.exists():
        return available_maps

    # Iterate through subdirectories
    for category_dir in sorted(maps_folder.iterdir()):
        if category_dir.is_dir():
            category_name = category_dir.name
            map_files = []

            # Get all .txt files in the category
            for map_file in sorted(category_dir.glob("*.txt")):
                map_name = map_file.stem  # filename without extension
                map_files.append((map_name, str(map_file)))

            if map_files:
                available_maps[category_name] = map_files

    return available_maps
