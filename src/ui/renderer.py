"""Rendering and drawing functions for the visualization."""

import pygame
import math
from ..cls_data import Data
from ..utils.geometry import scale_to_screen
from ..utils.colors import parse_color

HUB_RADIUS = 10


def draw_connections(screen, data: Data, path: list[str] | None,
                     min_x: float, max_x: float, min_y: float, max_y: float,
                     window_width: int, window_height: int) -> None:
    """Draw connection lines between hubs."""
    for connection in data.connections:
        hub_a = data.hubs[connection.hub_a]
        hub_b = data.hubs[connection.hub_b]

        # Scale positions to screen coordinates
        screen_x_a, screen_y_a = scale_to_screen(
            hub_a.x, hub_a.y,
            min_x, max_x, min_y, max_y,
            window_width, window_height
        )
        screen_x_b, screen_y_b = scale_to_screen(
            hub_b.x, hub_b.y,
            min_x, max_x, min_y, max_y,
            window_width, window_height
        )

        # Check if this connection is part of the path
        is_in_path = False
        if path:
            for i in range(len(path) - 1):
                if connection.contains(path[i], path[i + 1]):
                    is_in_path = True
                    break

        # Draw line between hubs
        line_color = (255, 0, 0) if is_in_path else (128, 128, 128)
        line_width = 4 if is_in_path else 2
        pygame.draw.line(screen, line_color, (screen_x_a, screen_y_a), (screen_x_b, screen_y_b), line_width)


def draw_hubs(screen, data: Data, hub_gif_frames: list | None, hub_gif_duration: int,
              turn_elapsed: int, min_x: float, max_x: float, min_y: float, max_y: float,
              window_width: int, window_height: int, scheduler=None) -> None:
    """Draw hubs and their labels."""
    for hub in data.hubs.values():
        # Scale position to screen coordinates
        screen_x, screen_y = scale_to_screen(
            hub.x, hub.y,
            min_x, max_x, min_y, max_y,
            window_width, window_height
        )

        # Draw hub sprite if available
        if hub_gif_frames:
            frame_index = int((turn_elapsed / hub_gif_duration) * len(hub_gif_frames)) % len(hub_gif_frames)
            frame = hub_gif_frames[frame_index]
            screen.blit(frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height() // 2))
        else:
            # Fallback to circle if GIF not available
            hub_color = parse_color(hub.color)
            pygame.draw.circle(screen, hub_color, (screen_x, screen_y), HUB_RADIUS)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), HUB_RADIUS, 2)

        # Draw hub name label
        font = pygame.font.Font(None, 24)
        text_surface = font.render(hub.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(text_surface, text_rect)

        # Draw drone count at hub
        if scheduler:
            drone_count = scheduler.get_hub_occupancy(hub.name)
            if drone_count > 0:
                count_font = pygame.font.Font(None, 20)
                count_text = count_font.render(f"[{drone_count}]", True, (255, 0, 0))
                count_rect = count_text.get_rect(topleft=(screen_x + HUB_RADIUS + 5, screen_y - 10))
                screen.blit(count_text, count_rect)


def draw_drones(screen, data: Data, scheduler, path: list[str] | None,
                gif_frames: list | None, turn_elapsed: int, turn_duration_ms: int,
                min_x: float, max_x: float, min_y: float, max_y: float,
                window_width: int, window_height: int) -> None:
    """Draw drones on their current hubs."""
    if not scheduler:
        return

    for drone in scheduler.drones:
        if not drone.completed:
            # Get drone's current hub
            # For MultiPathDroneScheduler, use drone.current_hub directly
            # For DroneScheduler, look it up from the path
            if hasattr(scheduler, 'get_drone_path'):
                # MultiPathDroneScheduler
                current_hub_name = drone.current_hub
            else:
                # DroneScheduler
                if not path:
                    continue
                current_hub_name = path[drone.path_index]

            current_hub = data.hubs[current_hub_name]

            # Scale position to screen coordinates
            screen_x, screen_y = scale_to_screen(
                current_hub.x, current_hub.y,
                min_x, max_x, min_y, max_y,
                window_width, window_height
            )

            # Draw drone offset to avoid overlap
            offset_angle = (drone.drone_id * 360 / max(len(scheduler.drones), 1)) * math.pi / 180
            offset_dist = 20
            drone_x = int(screen_x + offset_dist * math.cos(offset_angle))
            drone_y = int(screen_y + offset_dist * math.sin(offset_angle))

            if gif_frames:
                # Draw animated GIF frame
                frame_index = int((turn_elapsed / turn_duration_ms) * len(gif_frames)) % len(gif_frames)
                frame = gif_frames[frame_index]
                screen.blit(frame, (drone_x - frame.get_width() // 2, drone_y - frame.get_height() // 2))
            else:
                # Fallback to circle if GIF not available
                pygame.draw.circle(screen, (0, 0, 255), (drone_x, drone_y), 4)
                pygame.draw.circle(screen, (0, 0, 0), (drone_x, drone_y), 4, 1)


def draw_simulation_info(screen, scheduler, speed_multiplier: float = 1.0, is_complete: bool = False) -> None:
    """Draw simulation info text (turn number and drone completion status)."""
    if not scheduler:
        return

    info_font = pygame.font.Font(None, 20)
    turn_text = info_font.render(f"Turn: {scheduler.current_turn}", True, (0, 0, 0))
    completed_text = info_font.render(
        f"Drones completed: {sum(1 for d in scheduler.drones if d.completed)}/{len(scheduler.drones)}",
        True, (0, 0, 0)
    )
    speed_text = info_font.render(f"Speed: {speed_multiplier:.1f}x (↑/↓ to adjust)", True, (0, 100, 200))
    screen.blit(turn_text, (10, 10))
    screen.blit(completed_text, (10, 35))
    screen.blit(speed_text, (10, 60))

    # Display final score if simulation is complete
    if is_complete:
        score_font = pygame.font.Font(None, 40)
        score_text = score_font.render(f"SCORE: {scheduler.current_turn} turns", True, (0, 150, 0))
        score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

        # Draw semi-transparent background for readability
        bg_rect = score_rect.inflate(40, 40)
        background = pygame.Surface((bg_rect.width, bg_rect.height))
        background.set_alpha(220)
        background.fill((255, 255, 255))
        screen.blit(background, bg_rect)

        # Draw score text
        screen.blit(score_text, score_rect)
