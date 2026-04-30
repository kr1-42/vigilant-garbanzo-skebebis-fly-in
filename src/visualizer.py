import pygame
from .cls_data import Data, Hub

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
HUB_RADIUS = 15
PADDING = 2


def parse_color(color_name: str | None) -> tuple[int, int, int]:
    """Convert color name to RGB tuple."""
    if color_name is None:
        return DEFAULT_COLOR
    color_lower = color_name.lower().strip()
    return COLOR_MAP.get(color_lower, DEFAULT_COLOR)


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


def visualize(data: Data) -> None:
    """Create a pygame window and visualize the hubs as circles."""
    pygame.init()

    # Get bounds
    min_x, max_x, min_y, max_y = get_canvas_bounds(data.hubs)

    # Calculate screen size based on bounds
    bounds_width = max_x - min_x if max_x != min_x else 100
    bounds_height = max_y - min_y if max_y != min_y else 100
    aspect_ratio = bounds_width / bounds_height if bounds_height != 0 else 1

    # Set window size (with padding)
    window_height = 800
    window_width = int(window_height * aspect_ratio)
    window_width = max(window_width, 600)

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Drone Network Visualization")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen
        screen.fill((255, 255, 255))

        # Draw hubs
        for hub in data.hubs.values():
            # Scale position to screen coordinates
            screen_x, screen_y = scale_to_screen(
                hub.x, hub.y,
                min_x, max_x, min_y, max_y,
                window_width, window_height
            )

            # Get hub color
            hub_color = parse_color(hub.color)

            # Draw circle
            pygame.draw.circle(screen, hub_color, (screen_x, screen_y), HUB_RADIUS)

            # Draw outline
            pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), HUB_RADIUS, 2)

            # Draw hub name label
            font = pygame.font.Font(None, 24)
            text_surface = font.render(hub.name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
