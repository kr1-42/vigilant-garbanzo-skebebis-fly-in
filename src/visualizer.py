"""Main visualization module."""

import pygame
from typing import cast
from .cls_data import Data
from .algo import (
    check_path_feasibility,
    MultiPathDroneScheduler,
    optimize_path_strategy,
)
from .simulation.integration import (
    SimulationWithTracking,
    SimulationWithMultiPath,
)
from .utils.assets import load_gif_frames
from .utils.geometry import get_canvas_bounds
from .loaders.map_loader import load_map_from_file, get_available_maps
from .ui.renderer import (
    draw_connections,
    draw_hubs,
    draw_drones,
    draw_simulation_info,
    draw_end_screen_with_menu,
)
from .ui.zone_info import ZoneInfoPopup, HoverDetector

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

DRONE_GIF = "sprites/FO1_Fire_critical_hit.gif"
HUB_GIF = "sprites/Maroboaa_se.gif"

# Available hub sprites (excluding FO1_Fire_critical_hit.gif)
AVAILABLE_HUB_SPRITES = [
    "sprites/Maroboaa_se.gif",
    "sprites/Jacoren_death_animation.gif",
    "sprites/Mutant1.gif",
]

DRONE_GIF_SIZE = (60, 60)
HUB_GIF_SIZE = (40, 40)

DEFAULT_GIF_DURATION = 500


def load_hub_sprite(sprite_index: int) -> tuple[list | None, int, str]:
    """Load hub sprite by index from AVAILABLE_HUB_SPRITES.

    Args:
        sprite_index: Index in AVAILABLE_HUB_SPRITES

    Returns:
        Tuple of (frames, duration_ms, sprite_name)
    """
    if 0 <= sprite_index < len(AVAILABLE_HUB_SPRITES):
        sprite_path = AVAILABLE_HUB_SPRITES[sprite_index]
        sprite_name = sprite_path.split("/")[-1].replace(".gif", "")

        hub_gif_result = load_gif_frames(
            sprite_path,
            max_width=HUB_GIF_SIZE[0],
            max_height=HUB_GIF_SIZE[1],
        )
        frames = hub_gif_result[0] if hub_gif_result else None
        duration = (
            hub_gif_result[1] if hub_gif_result else DEFAULT_GIF_DURATION
        )

        return frames, duration, sprite_name

    return None, DEFAULT_GIF_DURATION, "unknown"


def visualize(data: Data) -> None:
    """Create a pygame window and visualize the hubs and drone movements.

    Raises:
        ValueError: If the configuration is invalid or no path can be found
        FileNotFoundError: If sprite files cannot be loaded
    """
    pygame.init()

    try:
        # Get bounds
        min_x, max_x, min_y, max_y = get_canvas_bounds(data.hubs)

        # Create window
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Drone Network Visualization")
        clock = pygame.time.Clock()

        # Load sprites
        gif_result = load_gif_frames(
            DRONE_GIF,
            max_width=DRONE_GIF_SIZE[0],
            max_height=DRONE_GIF_SIZE[1],
        )
        gif_frames = gif_result[0] if gif_result else None
        gif_duration = gif_result[1] if gif_result else DEFAULT_GIF_DURATION

        # Initialize hub sprite with first available sprite
        current_hub_sprite_index = 0
        (
            hub_gif_frames,
            hub_gif_duration,
            current_hub_sprite_name,
        ) = load_hub_sprite(current_hub_sprite_index)

        # Initialize simulation state
        turn_elapsed = 0
        base_turn_duration_ms = max(gif_duration, 100) if gif_frames else 100
        speed_multiplier = 10.0

        # Initialize hover popup system
        zone_info_popup = ZoneInfoPopup(data)
        hover_detector = HoverDetector(hub_radius=HUB_GIF_SIZE[0] // 2)

        def get_turn_duration() -> int:
            """Calculate turn duration based on current speed multiplier."""
            return int(base_turn_duration_ms / speed_multiplier)

        path = None
        paths: list[list[str]] = []
        scheduler = None
        path_feasible = False

        # Use optimized strategy to choose between single and multiple paths
        best_paths, strategy = optimize_path_strategy(data)

        if not best_paths:
            raise ValueError("No valid path found from start to end hub")

        # Ensure proper typing
        if strategy == "multiple":
            # Multiple paths: best_paths is list[list[str]]
            paths = cast(list[list[str]], best_paths)
            path = paths[0] if paths else None

            if path:
                # Check feasibility of primary path
                feasibility = check_path_feasibility(path, data)
                path_feasible = feasibility["feasible"]
                if not path_feasible:
                    print(f"Violations: {feasibility['violations']}")

                # Create multi-path scheduler and tracking
                scheduler = MultiPathDroneScheduler(data, paths)
                tracking = SimulationWithMultiPath(data, paths, scheduler)
            else:
                raise ValueError("No valid path found from start to end hub")
        else:
            # Single path strategy: best_paths is list[str]
            path = cast(list[str], best_paths)
            paths = [path]

            # Check capacity constraints
            if path:
                feasibility = check_path_feasibility(path, data)
                path_feasible = feasibility["feasible"]
                if not path_feasible:
                    print(f"Violations: {feasibility['violations']}")

                # Create simulation with tracking
                tracking = SimulationWithTracking(data, path)
                scheduler = tracking.scheduler
            else:
                raise ValueError("No valid path found from start to end hub")

        # Main loop
        running = True
        simulation_complete = False
        selected_menu_index = 0
        available_maps = get_available_maps()

        # Flatten maps for selection
        menu_items = []
        for category in sorted(available_maps.keys()):
            menu_items.append(("header", category))
            for map_name, map_path in available_maps[category]:
                menu_items.append(("map", (map_name, map_path)))

        while running:
            dt = clock.tick(6000)  # 60 FPS
            turn_elapsed += dt

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if simulation_complete:
                            running = False
                        else:
                            running = False
                    elif event.key == pygame.K_UP and not simulation_complete:
                        speed_multiplier = min(speed_multiplier + 0.5, 20)
                    elif (
                        event.key == pygame.K_DOWN and not simulation_complete
                    ):
                        speed_multiplier = max(speed_multiplier - 0.5, 0.25)
                    # Hub sprite switching
                    elif (
                        event.key == pygame.K_LEFTBRACKET
                        and not simulation_complete
                    ):
                        current_hub_sprite_index = (
                            current_hub_sprite_index - 1
                        ) % len(AVAILABLE_HUB_SPRITES)
                        (
                            hub_gif_frames,
                            hub_gif_duration,
                            current_hub_sprite_name,
                        ) = load_hub_sprite(current_hub_sprite_index)
                    elif (
                        event.key == pygame.K_RIGHTBRACKET
                        and not simulation_complete
                    ):
                        current_hub_sprite_index = (
                            current_hub_sprite_index + 1
                        ) % len(AVAILABLE_HUB_SPRITES)
                        (
                            hub_gif_frames,
                            hub_gif_duration,
                            current_hub_sprite_name,
                        ) = load_hub_sprite(current_hub_sprite_index)
                    # Menu navigation (when simulation is complete)
                    elif event.key == pygame.K_UP and simulation_complete:
                        selected_menu_index = (selected_menu_index - 1) % len(
                            menu_items
                        )
                        while menu_items[selected_menu_index][0] == "header":
                            selected_menu_index = (
                                selected_menu_index - 1
                            ) % len(menu_items)
                    elif event.key == pygame.K_DOWN and simulation_complete:
                        selected_menu_index = (selected_menu_index + 1) % len(
                            menu_items
                        )
                        while menu_items[selected_menu_index][0] == "header":
                            selected_menu_index = (
                                selected_menu_index + 1
                            ) % len(menu_items)
                    elif event.key == pygame.K_RETURN and simulation_complete:
                        if menu_items[selected_menu_index][0] == "map":
                            selected_map = menu_items[selected_menu_index][1][
                                1
                            ]
                            new_data = load_map_from_file(selected_map)
                            if new_data:
                                pygame.quit()
                                visualize(new_data)
                                return
                            else:
                                print("Failed to load selected map")

            # Check if all drones have completed
            if (
                tracking
                and tracking.all_drones_completed()
                and not simulation_complete
            ):
                print("\n=== SIMULATION COMPLETE ===")
                print(f"Total turns: {tracking.current_turn}")
                print()
                simulation_complete = True

            # Advance simulation only when turn duration has elapsed
            if tracking and not tracking.all_drones_completed():
                if turn_elapsed >= get_turn_duration():
                    tracking.advance_turn()
                    turn_elapsed = 0

            # Draw simulation or end screen
            if simulation_complete:
                # Draw integrated end screen with metrics and map selection
                draw_end_screen_with_menu(
                    screen,
                    tracking.scheduler,
                    available_maps,
                    selected_menu_index,
                )
            else:
                # Draw normal simulation
                # Clear screen
                screen.fill((255, 255, 255))

                # Draw all elements
                draw_connections(
                    screen,
                    data,
                    path,
                    min_x,
                    max_x,
                    min_y,
                    max_y,
                    WINDOW_WIDTH,
                    WINDOW_HEIGHT,
                )
                draw_hubs(
                    screen,
                    data,
                    hub_gif_frames,
                    hub_gif_duration,
                    turn_elapsed,
                    min_x,
                    max_x,
                    min_y,
                    max_y,
                    WINDOW_WIDTH,
                    WINDOW_HEIGHT,
                    tracking.scheduler if tracking else None,
                    hover_detector,
                )
                draw_drones(
                    screen,
                    data,
                    tracking.scheduler if tracking else None,
                    path,
                    gif_frames,
                    turn_elapsed,
                    get_turn_duration(),
                    min_x,
                    max_x,
                    min_y,
                    max_y,
                    WINDOW_WIDTH,
                    WINDOW_HEIGHT,
                )
                draw_simulation_info(
                    screen,
                    tracking.scheduler if tracking else None,
                    speed_multiplier,
                    simulation_complete,
                    current_hub_sprite_name,
                )

                # Draw hover popup if mouse is over a hub
                mouse_pos = pygame.mouse.get_pos()
                hovered_hub = hover_detector.get_hovered_hub(mouse_pos, data)
                if hovered_hub:
                    zone_info_popup.draw_popup(
                        screen,
                        mouse_pos,
                        hovered_hub,
                        tracking.scheduler if tracking else None,
                    )

            pygame.display.flip()

    finally:
        pygame.quit()
