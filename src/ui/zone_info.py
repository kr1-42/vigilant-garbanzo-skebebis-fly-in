"""Zone information popup display for hover interactions."""

import pygame
from typing import Optional
from ..cls_data import Data, Hub


class ZoneInfoPopup:
    """Displays zone information when hovering over a hub."""

    def __init__(self, data: Data):
        self.data = data
        self.popup_width = 250
        self.popup_height = 200
        self.padding = 10
        self.line_height = 20
        self.bg_color = (240, 240, 240)
        self.border_color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        self.small_font = pygame.font.Font(None, 12)
        self.title_font = pygame.font.Font(None, 14)

    def get_zone_info(self, hub: Hub) -> dict:
        """Get detailed information about a zone/hub."""
        # Get connected hubs and their capacities
        connections_info = []
        for conn in self.data.connections:
            if conn.hub_a == hub.name:
                connections_info.append(
                    {"hub": conn.hub_b, "capacity": conn.max_link_capacity}
                )
            elif conn.hub_b == hub.name:
                connections_info.append(
                    {"hub": conn.hub_a, "capacity": conn.max_link_capacity}
                )

        # Map zone types to movement costs
        zone_costs = {
            "normal": 1,
            "blocked": float("inf"),
            "restricted": 2,
            "priority": 0.5,
        }

        return {
            "name": hub.name,
            "kind": hub.kind,
            "zone": hub.zone,
            "max_drones": hub.max_drones,
            "movement_cost": zone_costs.get(hub.zone, 1),
            "connections": connections_info,
        }

    def draw_popup(
        self,
        screen: pygame.Surface,
        mouse_pos: tuple[int, int],
        hub: Optional[Hub],
        scheduler=None,
    ) -> None:
        """Draw zone information popup at mouse position."""
        if not hub:
            return

        info = self.get_zone_info(hub)

        # Calculate popup position (offset from mouse)
        popup_x = mouse_pos[0] + 15
        popup_y = mouse_pos[1] + 15

        # Keep popup within screen bounds
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if popup_x + self.popup_width > screen_width:
            popup_x = screen_width - self.popup_width - 5
        if popup_y + self.popup_height > screen_height:
            popup_y = screen_height - self.popup_height - 5

        # Draw background
        popup_rect = pygame.Rect(
            popup_x, popup_y, self.popup_width, self.popup_height
        )
        pygame.draw.rect(screen, self.bg_color, popup_rect)
        pygame.draw.rect(screen, self.border_color, popup_rect, 2)

        # Draw title with zone kind
        y_offset = popup_y + self.padding
        title_text = self.title_font.render(
            f"{info['name']} ({info['kind']})", True, (0, 0, 150)
        )
        screen.blit(title_text, (popup_x + self.padding, y_offset))
        y_offset += self.line_height

        # Draw separator line
        pygame.draw.line(
            screen,
            self.border_color,
            (popup_x + self.padding, y_offset - 5),
            (popup_x + self.popup_width - self.padding, y_offset - 5),
            1,
        )

        # Draw zone type
        zone_color = self._get_zone_color(info["zone"])
        zone_text = self.small_font.render(
            f"Zone: {info['zone']}", True, zone_color
        )
        screen.blit(zone_text, (popup_x + self.padding, y_offset))
        y_offset += self.line_height

        # Draw movement cost with color coding
        cost_display = (
            f"∞"
            if info["movement_cost"] == float("inf")
            else f"{info['movement_cost']:.1f}"
        )
        cost_color = (
            (200, 0, 0)
            if info["movement_cost"] == float("inf")
            else (0, 100, 0)
        )
        cost_text = self.small_font.render(
            f"Move Cost: {cost_display}", True, cost_color
        )
        screen.blit(cost_text, (popup_x + self.padding, y_offset))
        y_offset += self.line_height

        # Draw capacity and occupancy
        if scheduler:
            occupancy = scheduler.get_hub_occupancy(hub.name)
            occupancy_str = f"{occupancy}/{info['max_drones']}"
            occupancy_color = (
                (200, 0, 0) if occupancy >= info["max_drones"] else (0, 100, 0)
            )
            capacity_text = self.small_font.render(
                f"Capacity: {occupancy_str}", True, occupancy_color
            )
        else:
            capacity_text = self.small_font.render(
                f"Max Drones: {info['max_drones']}", True, self.text_color
            )
        screen.blit(capacity_text, (popup_x + self.padding, y_offset))
        y_offset += self.line_height

        # Draw connections header
        if info["connections"]:
            connections_header = self.small_font.render(
                "Connected zones:", True, (0, 100, 0)
            )
            screen.blit(connections_header, (popup_x + self.padding, y_offset))
            y_offset += self.line_height

            for i, conn in enumerate(info["connections"][:2]):
                if (
                    y_offset + self.line_height
                    > popup_y + self.popup_height - self.padding
                ):
                    break
                conn_text = self.small_font.render(
                    f"  → {conn['hub']} (cap: {conn['capacity']})",
                    True,
                    self.text_color,
                )
                screen.blit(conn_text, (popup_x + self.padding, y_offset))
                y_offset += self.line_height

            if len(info["connections"]) > 2:
                more_text = self.small_font.render(
                    f"  +{len(info['connections']) - 2} more",
                    True,
                    (100, 100, 100),
                )
                screen.blit(more_text, (popup_x + self.padding, y_offset))

    def _get_zone_color(self, zone_type: str) -> tuple[int, int, int]:
        """Get color for zone type."""
        zone_colors = {
            "normal": (0, 0, 0),
            "blocked": (200, 0, 0),
            "restricted": (200, 100, 0),
            "priority": (0, 150, 0),
        }
        return zone_colors.get(zone_type, (0, 0, 0))


class HoverDetector:
    """Detects which hub the mouse is hovering over."""

    def __init__(self, hub_radius: int = 10):
        self.hub_positions = {}  # {hub_name: (screen_x, screen_y)}
        self.hub_radius = hub_radius

    def update_hub_position(
        self, hub_name: str, screen_x: int, screen_y: int
    ) -> None:
        """Update the screen position of a hub."""
        self.hub_positions[hub_name] = (screen_x, screen_y)

    def get_hovered_hub(
        self, mouse_pos: tuple[int, int], data: Data
    ) -> Optional[Hub]:
        """Get the hub at the current mouse position, if any."""
        mouse_x, mouse_y = mouse_pos

        for hub_name, (hub_x, hub_y) in self.hub_positions.items():
            distance = ((mouse_x - hub_x) ** 2 + (mouse_y - hub_y) ** 2) ** 0.5
            if distance <= self.hub_radius + 10:  # Add 10 pixel tolerance
                return data.hubs[hub_name]

        return None
