"""Main visualization module."""

import pygame
from typing import cast
from .cls_data import Data
from .algo import check_path_feasibility, dijkstra_find_path, find_multiple_paths, MultiPathDroneScheduler, optimize_path_strategy
from .simulation.integration import SimulationWithTracking, SimulationWithMultiPath
from .utils.assets import load_gif_frames
from .utils.geometry import get_canvas_bounds
from .loaders.map_loader import load_map_from_file
from .ui.menu import display_map_menu
from .ui.renderer import draw_connections, draw_hubs, draw_drones, draw_simulation_info

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

DRONE_GIF = "sprites/Mutant1.gif"
HUB_GIF = "sprites/Maroboaa_se.gif"

DRONE_GIF_SIZE = (60, 60)
HUB_GIF_SIZE = (40, 40)

DEFAULT_GIF_DURATION = 500


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
        gif_result = load_gif_frames(DRONE_GIF, max_width=DRONE_GIF_SIZE[0], max_height=DRONE_GIF_SIZE[1])
        gif_frames = gif_result[0] if gif_result else None
        gif_duration = gif_result[1] if gif_result else DEFAULT_GIF_DURATION

        hub_gif_result = load_gif_frames(HUB_GIF, max_width=HUB_GIF_SIZE[0], max_height=HUB_GIF_SIZE[1])
        hub_gif_frames = hub_gif_result[0] if hub_gif_result else None
        hub_gif_duration = hub_gif_result[1] if hub_gif_result else DEFAULT_GIF_DURATION

        # Initialize simulation state
        turn_elapsed = 0
        base_turn_duration_ms = max(gif_duration, 100) if gif_frames else 100
        speed_multiplier = 10

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
        show_menu = False

        while running:
            dt = clock.tick(6000)  # 60 FPS
            turn_elapsed += dt

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Speed control: UP arrow to speed up, DOWN arrow to slow down
                    elif event.key == pygame.K_UP:
                        speed_multiplier = min(speed_multiplier + 0.5, 20)  # Max 7.5x speed
                    elif event.key == pygame.K_DOWN:
                        speed_multiplier = max(speed_multiplier - 0.5, 0.25)  # Min 0.25x speed

            # Check if all drones have completed
            if tracking and tracking.all_drones_completed() and not show_menu:
                print("\n=== SIMULATION COMPLETE ===")
                print(f"Total turns: {tracking.current_turn}")
                print()
                show_menu = True

            # Show menu if all drones completed
            if show_menu:
                selected_map = display_map_menu(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
                if selected_map:
                    # Load new map and recursively visualize it
                    new_data = load_map_from_file(selected_map)
                    if new_data:
                        pygame.quit()
                        visualize(new_data)
                        return
                    else:
                        print("Failed to load selected map")
                        show_menu = False
                else:
                    # User cancelled menu
                    running = False
            # Advance simulation only when turn duration has elapsed
            elif tracking and not tracking.all_drones_completed():
                if turn_elapsed >= get_turn_duration():
                    tracking.advance_turn()
                    turn_elapsed = 0

            # Only draw simulation if menu is not being shown
            if not show_menu:
                # Clear screen
                screen.fill((255, 255, 255))

                # Draw all elements
                draw_connections(screen, data, path, min_x, max_x, min_y, max_y, WINDOW_WIDTH, WINDOW_HEIGHT)
                draw_hubs(screen, data, hub_gif_frames, hub_gif_duration, turn_elapsed,
                          min_x, max_x, min_y, max_y, WINDOW_WIDTH, WINDOW_HEIGHT, tracking.scheduler if tracking else None)
                draw_drones(screen, data, tracking.scheduler if tracking else None, path, gif_frames, turn_elapsed, get_turn_duration(),
                            min_x, max_x, min_y, max_y, WINDOW_WIDTH, WINDOW_HEIGHT)
                draw_simulation_info(screen, tracking.scheduler if tracking else None, speed_multiplier, show_menu)
                pygame.display.flip()

    finally:
        pygame.quit()
