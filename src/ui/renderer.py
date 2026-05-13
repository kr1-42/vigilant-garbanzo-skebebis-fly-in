"""Rendering and drawing functions for the visualization."""

import pygame
import math
from ..cls_data import Data
from ..utils.geometry import scale_to_screen
from ..utils.colors import parse_color

HUB_RADIUS = 10


def draw_connections(
    screen,
    data: Data,
    path: list[str] | None,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    window_width: int,
    window_height: int,
) -> None:
    """Draw connection lines between hubs."""
    for connection in data.connections:
        hub_a = data.hubs[connection.hub_a]
        hub_b = data.hubs[connection.hub_b]

        # Scale positions to screen coordinates
        screen_x_a, screen_y_a = scale_to_screen(
            hub_a.x,
            hub_a.y,
            min_x,
            max_x,
            min_y,
            max_y,
            window_width,
            window_height,
        )
        screen_x_b, screen_y_b = scale_to_screen(
            hub_b.x,
            hub_b.y,
            min_x,
            max_x,
            min_y,
            max_y,
            window_width,
            window_height,
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
        pygame.draw.line(
            screen,
            line_color,
            (screen_x_a, screen_y_a),
            (screen_x_b, screen_y_b),
            line_width,
        )


def draw_hubs(
    screen,
    data: Data,
    hub_gif_frames: list | None,
    hub_gif_duration: int,
    turn_elapsed: int,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    window_width: int,
    window_height: int,
    scheduler=None,
    hover_detector=None,
) -> None:
    """Draw hubs and their labels. Returns hover detector updated with hub
    positions.
    """
    for hub in data.hubs.values():
        # Scale position to screen coordinates
        screen_x, screen_y = scale_to_screen(
            hub.x,
            hub.y,
            min_x,
            max_x,
            min_y,
            max_y,
            window_width,
            window_height,
        )

        # Update hover detector with hub position
        if hover_detector:
            hover_detector.update_hub_position(
                hub.name, int(screen_x), int(screen_y)
            )

        # Draw hub sprite if available
        if hub_gif_frames:
            frame_index = int(
                (turn_elapsed / hub_gif_duration) * len(hub_gif_frames)
            ) % len(hub_gif_frames)
            frame = hub_gif_frames[frame_index]
            screen.blit(
                frame,
                (
                    screen_x - frame.get_width() // 2,
                    screen_y - frame.get_height() // 2,
                ),
            )
        else:
            # Fallback to circle if GIF not available
            hub_color = parse_color(hub.color)
            pygame.draw.circle(
                screen, hub_color, (screen_x, screen_y), HUB_RADIUS
            )
            pygame.draw.circle(
                screen, (0, 0, 0), (screen_x, screen_y), HUB_RADIUS, 2
            )

        # Draw small hub name label (optional, can be hidden by default)
        small_font = pygame.font.Font(None, 10)
        text_surface = small_font.render(hub.name, True, (100, 100, 100))
        text_rect = text_surface.get_rect(
            center=(screen_x, screen_y + HUB_RADIUS + 8)
        )
        screen.blit(text_surface, text_rect)

        # Draw drone count at hub
        if scheduler:
            drone_count = scheduler.get_hub_occupancy(hub.name)
            if drone_count > 0:
                count_font = pygame.font.Font(None, 20)
                count_text = count_font.render(
                    f"[{drone_count}]", True, (255, 0, 0)
                )
                count_rect = count_text.get_rect(
                    topleft=(screen_x + HUB_RADIUS + 5, screen_y - 10)
                )
                screen.blit(count_text, count_rect)


def draw_drones(
    screen,
    data: Data,
    scheduler,
    path: list[str] | None,
    gif_frames: list | None,
    turn_elapsed: int,
    turn_duration_ms: int,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    window_width: int,
    window_height: int,
) -> None:
    """Draw drones on their current hubs."""
    if not scheduler:
        return

    for drone in scheduler.drones:
        if not drone.completed:
            # Get drone's current hub
            # For MultiPathDroneScheduler, use drone.current_hub directly
            # For DroneScheduler, look it up from the path
            if hasattr(scheduler, "get_drone_path"):
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
                current_hub.x,
                current_hub.y,
                min_x,
                max_x,
                min_y,
                max_y,
                window_width,
                window_height,
            )

            # Draw drone offset to avoid overlap
            offset_angle = (
                (drone.drone_id * 360 / max(len(scheduler.drones), 1))
                * math.pi
                / 180
            )
            offset_dist = 20
            drone_x = int(screen_x + offset_dist * math.cos(offset_angle))
            drone_y = int(screen_y + offset_dist * math.sin(offset_angle))

            if gif_frames:
                # Draw animated GIF frame
                frame_index = int(
                    (turn_elapsed / turn_duration_ms) * len(gif_frames)
                ) % len(gif_frames)
                frame = gif_frames[frame_index]
                screen.blit(
                    frame,
                    (
                        drone_x - frame.get_width() // 2,
                        drone_y - frame.get_height() // 2,
                    ),
                )
            else:
                # Fallback to circle if GIF not available
                pygame.draw.circle(screen, (0, 0, 255), (drone_x, drone_y), 4)
                pygame.draw.circle(screen, (0, 0, 0), (drone_x, drone_y), 4, 1)


def draw_simulation_info(
    screen, scheduler, speed_multiplier: float = 1.0, is_complete: bool = False
) -> None:
    """Draw simulation info text (turn number, drone completion status
    , and performance metrics)."""
    if not scheduler:
        return

    info_font = pygame.font.Font(None, 18)
    small_font = pygame.font.Font(None, 14)

    turn_text = info_font.render(
        f"Turn: {scheduler.current_turn}", True, (0, 0, 0)
    )
    completed_count = sum(1 for d in scheduler.drones if d.completed)
    completed_text = info_font.render(
        f"Drones completed: {completed_count}/{len(scheduler.drones)}",
        True,
        (0, 0, 0),
    )
    speed_text = small_font.render(
        f"Speed: {speed_multiplier:.1f}x (↑/↓ to adjust)", True, (0, 100, 200)
    )

    screen.blit(turn_text, (10, 10))
    screen.blit(completed_text, (10, 35))
    screen.blit(speed_text, (10, 55))

    # Calculate and display performance metrics
    if scheduler.current_turn > 0 and len(scheduler.drones) > 0:
        # Drones moved per turn (efficiency)
        total_movements = sum(
            d.path_index for d in scheduler.drones if d.completed
        )
        avg_efficiency = (
            total_movements / scheduler.current_turn
            if scheduler.current_turn > 0
            else 0
        )
        efficiency_text = small_font.render(
            f"Avg drones/turn: {avg_efficiency:.1f}", True, (0, 100, 0)
        )
        screen.blit(efficiency_text, (10, 75))

        # Average turns per drone
        completed_drones = [d for d in scheduler.drones if d.completed]
        if completed_drones:
            avg_turns = scheduler.current_turn / len(completed_drones)
            avg_turns_text = small_font.render(
                f"Avg turns/drone: {avg_turns:.1f}", True, (100, 0, 0)
            )
            screen.blit(avg_turns_text, (10, 95))

    # Display final score if simulation is complete
    if is_complete:
        score_font = pygame.font.Font(None, 48)
        metrics_font = pygame.font.Font(None, 20)
        label_font = pygame.font.Font(None, 16)

        # Calculate final metrics
        completed_count = sum(1 for d in scheduler.drones if d.completed)
        total_movements = sum(
            d.path_index for d in scheduler.drones if d.completed
        )
        avg_efficiency = (
            total_movements / scheduler.current_turn
            if scheduler.current_turn > 0
            else 0
        )
        avg_turns = (
            scheduler.current_turn / completed_count
            if completed_count > 0
            else 0
        )

        # Create result panel
        panel_width = 400
        panel_height = 280
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2

        # Draw background panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        background = pygame.Surface((panel_width, panel_height))
        background.set_alpha(240)
        background.fill((255, 255, 255))
        screen.blit(background, panel_rect)

        # Draw border
        pygame.draw.rect(screen, (0, 150, 0), panel_rect, 3)

        # Draw title
        y_offset = panel_y + 20
        title_text = score_font.render(
            "SIMULATION COMPLETE", True, (0, 150, 0)
        )
        title_rect = title_text.get_rect(
            center=(screen.get_width() // 2, y_offset)
        )
        screen.blit(title_text, title_rect)
        y_offset += 60

        # Draw separator line
        pygame.draw.line(
            screen,
            (200, 200, 200),
            (panel_x + 20, y_offset),
            (panel_x + panel_width - 20, y_offset),
            2,
        )
        y_offset += 15

        # Draw score (primary metric)
        score_text = metrics_font.render(
            f"Total Turns (Score): {scheduler.current_turn}", True, (0, 100, 0)
        )
        score_text_rect = score_text.get_rect(
            center=(screen.get_width() // 2, y_offset)
        )
        screen.blit(score_text, score_text_rect)
        y_offset += 35

        # Draw completion status
        completion_text = label_font.render(
            f"Drones Completed: {completed_count}/{len(scheduler.drones)}",
            True,
            (0, 0, 0),
        )
        completion_rect = completion_text.get_rect(
            center=(screen.get_width() // 2, y_offset)
        )
        screen.blit(completion_text, completion_rect)
        y_offset += 30

        # Draw efficiency metric
        efficiency_text = label_font.render(
            f"Avg Drones/Turn: {avg_efficiency:.2f}", True, (0, 0, 150)
        )
        efficiency_rect = efficiency_text.get_rect(
            center=(screen.get_width() // 2, y_offset)
        )
        screen.blit(efficiency_text, efficiency_rect)
        y_offset += 30

        # Draw average turns per drone
        turns_per_drone_text = label_font.render(
            f"Avg Turns/Drone: {avg_turns:.2f}", True, (150, 0, 0)
        )
        turns_rect = turns_per_drone_text.get_rect(
            center=(screen.get_width() // 2, y_offset)
        )
        screen.blit(turns_per_drone_text, turns_rect)
        y_offset += 35

        # Draw instruction text
        instr_font = pygame.font.Font(None, 14)
        instr_text = instr_font.render(
            "Select another map to continue or close the window",
            True,
            (100, 100, 100),
        )
        instr_rect = instr_text.get_rect(
            center=(screen.get_width() // 2, y_offset)
        )
        screen.blit(instr_text, instr_rect)


def draw_end_screen_with_menu(
    screen, scheduler, available_maps: dict, selected_index: int
) -> int:
    """Draw combined end screen with statistics and map selection menu.

    Returns the currently selected map index.
    """
    if not scheduler:
        return selected_index

    screen.fill((35, 35, 35))

    # Fonts
    title_font = pygame.font.Font(None, 48)
    metrics_font = pygame.font.Font(None, 18)
    menu_header_font = pygame.font.Font(None, 28)
    menu_item_font = pygame.font.Font(None, 22)
    instr_font = pygame.font.Font(None, 14)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Calculate final metrics
    completed_count = sum(1 for d in scheduler.drones if d.completed)
    total_movements = sum(
        d.path_index for d in scheduler.drones if d.completed
    )
    avg_efficiency = (
        total_movements / scheduler.current_turn
        if scheduler.current_turn > 0
        else 0
    )
    avg_turns = (
        scheduler.current_turn / completed_count if completed_count > 0 else 0
    )

    # ===== TOP SECTION: STATISTICS =====
    y_offset = 20

    # Title
    title_text = title_font.render("SIMULATION COMPLETE", True, (0, 200, 100))
    title_rect = title_text.get_rect(center=(screen_width // 2, y_offset))
    screen.blit(title_text, title_rect)
    y_offset += 50

    # Separator line
    pygame.draw.line(
        screen,
        (100, 100, 100),
        (20, y_offset),
        (screen_width - 20, y_offset),
        2,
    )
    y_offset += 15

    # Metrics in a grid layout
    metrics_y = y_offset
    left_column = screen_width // 4
    right_column = 3 * screen_width // 4

    # Left column metrics
    score_text = metrics_font.render(
        f"Total Turns: {scheduler.current_turn}", True, (0, 200, 100)
    )
    screen.blit(
        score_text, (left_column - score_text.get_width() // 2, metrics_y)
    )

    completion_text = metrics_font.render(
        f"Drones: {completed_count}/{len(scheduler.drones)}",
        True,
        (100, 200, 255),
    )
    screen.blit(
        completion_text,
        (left_column - completion_text.get_width() // 2, metrics_y + 35),
    )

    # Right column metrics
    efficiency_text = metrics_font.render(
        f"Avg Drones/Turn: {avg_efficiency:.2f}", True, (100, 200, 255)
    )
    screen.blit(
        efficiency_text,
        (right_column - efficiency_text.get_width() // 2, metrics_y),
    )

    turns_text = metrics_font.render(
        f"Avg Turns/Drone: {avg_turns:.2f}", True, (255, 150, 100)
    )
    screen.blit(
        turns_text,
        (right_column - turns_text.get_width() // 2, metrics_y + 35),
    )

    y_offset += 90

    # ===== SEPARATOR =====
    pygame.draw.line(
        screen,
        (100, 100, 100),
        (20, y_offset),
        (screen_width - 20, y_offset),
        1,
    )
    y_offset += 20

    # ===== BOTTOM SECTION: MAP SELECTION MENU =====
    menu_title = menu_header_font.render(
        "Select Next Map", True, (255, 200, 0)
    )
    menu_title_rect = menu_title.get_rect(center=(screen_width // 2, y_offset))
    screen.blit(menu_title, menu_title_rect)
    y_offset += 45

    # Flatten maps into menu items
    menu_items = []
    for category in sorted(available_maps.keys()):
        menu_items.append(("header", category))
        for map_name, map_path in available_maps[category]:
            menu_items.append(("map", (map_name, map_path)))

    # Draw menu items
    max_menu_height = screen_height - y_offset - 50
    item_height = 35
    max_visible_items = max(5, int(max_menu_height / item_height))

    # Calculate start index for scrolling
    start_index = max(0, selected_index - max_visible_items // 2)
    end_index = min(len(menu_items), start_index + max_visible_items)

    for i in range(start_index, end_index):
        item_type, item_data = menu_items[i]

        if item_type == "header":
            # Category header
            text = menu_item_font.render(
                item_data.upper(), True, (255, 200, 0)
            )
            screen.blit(text, (50, y_offset))
            y_offset += item_height
        else:
            # Map item
            map_name, _ = item_data

            if i == selected_index:
                # Highlight selected item
                highlight_rect = pygame.Rect(
                    30, y_offset - 5, screen_width - 60, item_height - 5
                )
                pygame.draw.rect(screen, (100, 150, 255), highlight_rect)
                text = menu_item_font.render(
                    f"► {map_name}", True, (255, 255, 255)
                )
            else:
                text = menu_item_font.render(
                    f"  {map_name}", True, (180, 180, 180)
                )

            screen.blit(text, (50, y_offset))
            y_offset += item_height

    # Draw instructions at bottom
    instr_text = instr_font.render(
        "↑/↓: Navigate | ENTER: Select | ESC: Exit", True, (150, 150, 150)
    )
    instr_rect = instr_text.get_rect(
        center=(screen_width // 2, screen_height - 20)
    )
    screen.blit(instr_text, instr_rect)

    return selected_index
