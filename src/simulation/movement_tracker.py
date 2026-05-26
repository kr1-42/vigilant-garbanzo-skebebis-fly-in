"""Tracks drone movements for each turn of simulation."""

from typing import Dict, List


class DroneMovementTracker:
    """Tracks drone movements throughout the simulation."""

    def __init__(self, path: List[str], num_drones: int):
        """
        Initialize the movement tracker.

        Args:
            path: The path drones follow (List of hub names)
            num_drones: Total number of drones in simulation
        """
        self.path = path
        self.num_drones = num_drones
        self.movement_history: Dict[
            int, List[tuple[int, str]]
        ] = {}  # turn -> [(drone_id, destination)]
        self.current_turn = 0
        self.drone_positions: Dict[int, int] = {
            i: 0 for i in range(num_drones)
        }  # drone_id -> path_index
        self.drone_completed: set[int] = set()  # drone_ids that have completed

    def record_movement(
        self, drone_id: int, old_path_index: int, new_path_index: int
    ) -> None:
        """
        Record that a drone moved from one position to another.

        Args:
            drone_id: The unique drone identifier
            old_path_index: The drone's previous position index in the path
            new_path_index: The drone's new position index in the path
        """
        if self.current_turn not in self.movement_history:
            self.movement_history[self.current_turn] = []

        destination = self.path[new_path_index]
        self.movement_history[self.current_turn].append(
            (drone_id, destination)
        )
        self.drone_positions[drone_id] = new_path_index

        # Check if drone reached the end
        if new_path_index >= len(self.path) - 1:
            self.drone_completed.add(drone_id)

    def record_position(self, drone_id: int, path_index: int) -> None:
        """
        Record the current position of a drone for tracking.

        Args:
            drone_id: The unique drone identifier
            path_index: The drone's current position index in the path
        """
        if self.current_turn not in self.movement_history:
            self.movement_history[self.current_turn] = []

        destination = self.path[path_index]
        # Check if we already recorded this drone this turn
        # (avoid duplicates from record_movement calls)
        already_recorded = any(
            d[0] == drone_id for d in self.movement_history[self.current_turn]
        )
        if not already_recorded:
            self.movement_history[self.current_turn].append(
                (drone_id, destination)
            )
        self.drone_positions[drone_id] = path_index

        # Check if drone reached the end
        if path_index >= len(self.path) - 1:
            self.drone_completed.add(drone_id)

    def advance_turn(self) -> None:
        """Advance to the next turn."""
        self.current_turn += 1

    def get_movements_for_turn(self, turn: int) -> List[tuple[int, str]]:
        """
        Get all movements that occurred in a specific turn.

        Args:
            turn: The turn number

        Returns:
            List of (drone_id, destination) tuples
        """
        return self.movement_history.get(turn, [])

    def is_complete(self) -> bool:
        """Check if all drones have completed."""
        return len(self.drone_completed) == self.num_drones

    def get_all_movements(self) -> Dict[int, List[tuple[int, str]]]:
        """Get all recorded movements."""
        return self.movement_history
