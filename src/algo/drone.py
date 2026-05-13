from dataclasses import dataclass


@dataclass
class Drone:
    """Represents a single drone in the network."""

    drone_id: int
    current_hub: str  # Current location (hub name)
    path_index: int  # Index in the path where the drone is
    turns_at_hub: int  # Turns spent at current hub (waiting for cost)
    completed: bool = False  # True when drone reaches end hub
    initial_stagger: int = 0  # Stagger delay for this drone (preserved)

    def __repr__(self) -> str:
        return (
            f"Drone({self.drone_id}, at={self.current_hub}, "
            f"path_idx={self.path_index}, completed={self.completed})"
        )
