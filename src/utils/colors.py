"""Color utilities for the visualization."""

# Color mapping for named colors
COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
    "olive": (128, 128, 0),
    "lime": (0, 255, 0),
    "maroon": (128, 0, 0),
    "silver": (192, 192, 192),
}

DEFAULT_COLOR = (200, 200, 200)  # Light gray default


def parse_color(color_name: str | None) -> tuple[int, int, int]:
    """Convert color name to RGB tuple."""
    if color_name is None:
        return DEFAULT_COLOR
    color_lower = color_name.lower().strip()
    return COLOR_MAP.get(color_lower, DEFAULT_COLOR)
