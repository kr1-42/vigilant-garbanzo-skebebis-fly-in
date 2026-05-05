"""Map selection menu UI."""

import pygame
from ..loaders.map_loader import get_available_maps


def display_map_menu(screen, window_width: int, window_height: int) -> str | None:
    """Display a map selection menu and return the selected map file path.

    Returns the file path of the selected map, or None if user cancels.
    """
    available_maps = get_available_maps()

    if not available_maps:
        print("No maps found in maps/ folder")
        return None

    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 48)
    font_normal = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

    # Flatten maps into a single list with category headers
    menu_items = []  # List of (type, data) tuples where type is 'header' or 'map'

    for category in sorted(available_maps.keys()):
        menu_items.append(('header', category))
        for map_name, map_path in available_maps[category]:
            menu_items.append(('map', (map_name, map_path)))

    selected_index = 0
    selecting = True

    while selecting:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                    # Skip headers
                    while menu_items[selected_index][0] == 'header':
                        selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                    # Skip headers
                    while menu_items[selected_index][0] == 'header':
                        selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if menu_items[selected_index][0] == 'map':
                        return menu_items[selected_index][1][1]  # Return file path

        # Draw menu
        screen.fill((40, 40, 40))

        title = font_large.render("Select a Map", True, (255, 255, 255))
        screen.blit(title, (window_width // 2 - title.get_width() // 2, 30))

        y_offset = 120
        for i, (item_type, item_data) in enumerate(menu_items):
            if item_type == 'header':
                # Draw category header
                text = font_normal.render(item_data, True, (255, 200, 0))
                screen.blit(text, (50, y_offset))
                y_offset += 50
            else:
                # Draw map option
                map_name, _ = item_data
                if i == selected_index:
                    # Highlight selected item
                    pygame.draw.rect(screen, (100, 100, 255), (30, y_offset - 5, window_width - 60, 40))
                    text = font_normal.render(f"> {map_name}", True, (255, 255, 255))
                else:
                    text = font_normal.render(f"  {map_name}", True, (200, 200, 200))
                screen.blit(text, (50, y_offset))
                y_offset += 45

        # Draw instructions
        instructions = font_small.render("↑/↓: Navigate | ENTER: Select | ESC: Exit", True, (150, 150, 150))
        screen.blit(instructions, (window_width // 2 - instructions.get_width() // 2, window_height - 50))

        pygame.display.flip()

    return None
