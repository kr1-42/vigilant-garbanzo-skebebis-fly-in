"""Color utilities for the visualization."""

import pygame

DEFAULT_COLOR = (200, 200, 200)  # Light gray default


def parse_color(color_name: str | None) -> tuple[int, int, int]:
    """Convert any pygame-supported color name or value to an RGB tuple."""
    if color_name is None:
        return DEFAULT_COLOR
    try:
        color = pygame.Color(color_name.strip())
    except ValueError:
        return DEFAULT_COLOR
    return color.r, color.g, color.b
