"""Geometry and coordinate transformation utilities."""

from ..cls_data import Hub

PADDING = 50  # Increased to keep hubs and labels inside window


def get_canvas_bounds(hubs: dict[str, Hub]) -> tuple[float, float, float, float]:
    """Get min/max x and y coordinates from hubs."""
    if not hubs:
        return 0, 0, 100, 100

    x_coords = [hub.x for hub in hubs.values()]
    y_coords = [hub.y for hub in hubs.values()]

    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)

    return min_x, max_x, min_y, max_y


def scale_to_screen(
    x: float, y: float,
    min_x: float, max_x: float, min_y: float, max_y: float,
    screen_width: int, screen_height: int
) -> tuple[int, int]:
    """Convert world coordinates to screen coordinates."""
    # Normalize to 0-1 range
    if max_x == min_x:
        norm_x = 0.5
    else:
        norm_x = (x - min_x) / (max_x - min_x)

    if max_y == min_y:
        norm_y = 0.5
    else:
        norm_y = (y - min_y) / (max_y - min_y)

    # Map to screen with padding
    screen_x = int(PADDING + norm_x * (screen_width - 2 * PADDING))
    screen_y = int(PADDING + norm_y * (screen_height - 2 * PADDING))

    return screen_x, screen_y
