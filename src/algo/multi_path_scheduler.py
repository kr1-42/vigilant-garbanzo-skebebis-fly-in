"""Multi-path drone scheduler for managing drones across multiple paths."""

from ..cls_data import Data
from .drone import Drone
from .pathfinding import get_movement_cost, find_connection


class MultiPathDroneScheduler:
    """Manages drones across multiple independent paths."""

    def __init__(self, data: Data, paths: list[list[str]]) -> None:
        """
        Initialize multi-path scheduler.

        Args:
            data: The drone network configuration
            paths: List of paths, each as a list of hub names
        """
        self.data = data
        self.paths = paths
        self.total_drones_to_spawn = data.nb_drones
        self.next_drone_id = 0
        self.drones: list[Drone] = []
        self.drone_path_assignment: dict[
            int, int
        ] = {}  # drone_id -> path_index
        self.current_turn = 0

        # Limit drones to start hub capacity to prevent overflow
        start_hub_capacity = data.hubs[data.start_hub].max_drones
        initial_drones = min(data.nb_drones, start_hub_capacity)

        # Distribute initial drones across paths based on capacity
        self._distribute_initial_drones(initial_drones)

    def _distribute_initial_drones(self, num_drones: int) -> None:
        """Distribute initial drones across paths."""
        drone_idx = 0

        for path_idx, path in enumerate(self.paths):
            if drone_idx >= num_drones:
                break
            # Calculate how many drones can use this path
            # Limited by the smallest hub capacity along the path
            min_hub_capacity = min(
                self.data.hubs[hub].max_drones for hub in path
            )
            drones_for_path = min(
                min_hub_capacity, num_drones - drone_idx
            )

            # Create drones for this path with individual staggering
            for i in range(drones_for_path):
                stagger = (
                    drone_idx * 3
                ) % 16  # Even spacing prevents synchronized movement
                drone = Drone(
                    drone_id=drone_idx,
                    current_hub=self.data.start_hub,
                    path_index=0,
                    turns_at_hub=stagger,
                    initial_stagger=stagger,
                )
                self.drones.append(drone)
                self.drone_path_assignment[drone_idx] = path_idx
                drone_idx += 1
                self.next_drone_id = drone_idx

            if drone_idx >= num_drones:
                break

        # If not all drones could be assigned, add them to the best path
        if drone_idx < num_drones:
            best_path_idx = 0  # Use first path as fallback
            while drone_idx < num_drones:
                stagger = (
                    drone_idx * 3
                ) % 16  # Even spacing prevents synchronized movement
                drone = Drone(
                    drone_id=drone_idx,
                    current_hub=self.data.start_hub,
                    path_index=0,
                    turns_at_hub=stagger,
                    initial_stagger=stagger,
                )
                self.drones.append(drone)
                self.drone_path_assignment[drone_idx] = best_path_idx
                drone_idx += 1
                self.next_drone_id = drone_idx

    def get_drone_path(self, drone: Drone) -> list[str]:
        """Get the path assigned to a drone."""
        path_idx = self.drone_path_assignment[drone.drone_id]
        return self.paths[path_idx]

    def can_move_drone(self, drone: Drone) -> bool:
        """Check if a drone can move to the next hub on its path."""
        if drone.completed:
            return False

        path = self.get_drone_path(drone)
        if drone.path_index >= len(path) - 1:
            return False

        next_hub = path[drone.path_index + 1]

        # Check if drone has waited enough turns for movement cost
        movement_cost = get_movement_cost(next_hub, self.data)
        if drone.turns_at_hub < movement_cost:
            return False

        # Check hub capacity at next hub (count drones going to this hub)
        path_idx = self.drone_path_assignment[drone.drone_id]
        next_hub_occupancy = sum(
            1
            for d in self.drones
            if not d.completed
            and self.drone_path_assignment[d.drone_id] == path_idx
            and path[d.path_index] == next_hub
        )

        next_hub_obj = self.data.hubs[next_hub]
        if next_hub_occupancy >= next_hub_obj.max_drones:
            return False

        return True

    def advance_turn(self) -> None:
        """Advance simulation by one turn. Move drones individually.

        Handles:
        - Multiple disjoint paths
        - Hub capacity constraints (max_drones)
        - Connection capacity constraints (max_link_capacity)
        - FIFO movement by drone ID (prevents synchronized waves)
        """
        self.current_turn += 1

        # Increment turn counter for all active drones
        for drone in self.drones:
            if not drone.completed:
                drone.turns_at_hub += 1

        # Collect candidates: drones that have waited long enough to move
        candidates = []
        for drone in self.drones:
            if drone.completed:
                continue

            path = self.get_drone_path(drone)
            if drone.path_index >= len(path) - 1:
                continue

            # Check if drone has waited enough for movement cost
            next_hub = path[drone.path_index + 1]
            movement_cost = get_movement_cost(next_hub, self.data)
            if drone.turns_at_hub >= movement_cost:
                candidates.append(drone)

        # Sort candidates by drone ID for FIFO priority
        candidates.sort(key=lambda d: d.drone_id)

        # Track hub occupancy AFTER moves (excluding candidates leaving)
        hub_after_moves = {}
        for hub_name in self.data.hubs:
            # Count all non-moving, active drones
            hub_after_moves[hub_name] = sum(
                1
                for d in self.drones
                if d.current_hub == hub_name
                and not d.completed
                and d not in candidates
            )

        # Track connection usage AFTER moves
        def get_connection_key(hub_a: str, hub_b: str) -> tuple[str, str]:
            """Normalize connection key (bidirectional)."""
            return tuple(sorted([hub_a, hub_b]))  # type: ignore

        connection_usage_after = {}
        for conn in self.data.connections:
            connection_usage_after[
                get_connection_key(conn.hub_a, conn.hub_b)
            ] = 0

        # Move drones one at a time in priority order (by drone ID)
        drones_to_move = []
        for drone in candidates:
            path = self.get_drone_path(drone)
            current_hub = path[drone.path_index]
            next_hub = path[drone.path_index + 1]
            next_hub_obj = self.data.hubs[next_hub]

            # Check hub capacity
            if hub_after_moves[next_hub] >= next_hub_obj.max_drones:
                continue  # Hub is full, can't move

            # Check connection capacity
            conn_key = get_connection_key(current_hub, next_hub)
            if conn_key in connection_usage_after:
                conn = find_connection(current_hub, next_hub, self.data)
                if (
                    conn
                    and connection_usage_after[conn_key]
                    >= conn.max_link_capacity
                ):
                    continue  # Connection is full, can't move

            # This drone can move!
            drones_to_move.append(drone)
            hub_after_moves[next_hub] += 1
            if conn_key in connection_usage_after:
                connection_usage_after[conn_key] += 1

        # Move all approved drones simultaneously
        for drone in drones_to_move:
            path = self.get_drone_path(drone)
            drone.path_index += 1
            drone.current_hub = path[drone.path_index]
            # Restore drone's initial stagger to maintain spacing
            drone.turns_at_hub = drone.initial_stagger

            # Check if drone reached the end
            if drone.path_index >= len(path) - 1:
                drone.completed = True

        # Spawn new drones if capacity allows and we haven't spawned all yet
        self._spawn_new_drones()

    def _spawn_new_drones(self) -> None:
        """Spawn new drones at start hub if capacity allows."""
        if self.next_drone_id >= self.total_drones_to_spawn:
            return  # All drones already spawned

        start_hub_capacity = self.data.hubs[self.data.start_hub].max_drones
        start_hub_occupancy = self.get_hub_occupancy(self.data.start_hub)

        # Spawn as many drones as capacity allows
        while (
            self.next_drone_id < self.total_drones_to_spawn
            and start_hub_occupancy < start_hub_capacity
        ):
            # Assign to best path
            best_path_idx = 0
            stagger = (
                self.next_drone_id * 3
            ) % 16  # Even spacing prevents synchronized movement
            new_drone = Drone(
                drone_id=self.next_drone_id,
                current_hub=self.data.start_hub,
                path_index=0,
                turns_at_hub=stagger,
                initial_stagger=stagger,
            )
            self.drones.append(new_drone)
            self.drone_path_assignment[self.next_drone_id] = best_path_idx
            self.next_drone_id += 1
            start_hub_occupancy += 1

    def all_drones_completed(self) -> bool:
        """Check if all drones have completed."""
        return all(d.completed for d in self.drones)

    def get_hub_occupancy(self, hub_name: str) -> int:
        """Count how many active drones are at a hub."""
        return sum(
            1
            for d in self.drones
            if d.current_hub == hub_name and not d.completed
        )

    def get_completion_times(self) -> dict[int, int]:
        """Get the turn at which each drone completed."""
        times = {}
        for drone in self.drones:
            if drone.completed:
                times[drone.drone_id] = self.current_turn
        return times

    def get_drone_positions(self) -> dict[int, str]:
        """Get current hub position of each drone."""
        return {d.drone_id: d.current_hub for d in self.drones}
