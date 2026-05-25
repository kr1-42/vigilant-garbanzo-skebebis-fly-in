"""Drone scheduler implementations for managing drone movement."""

from ..cls_data import Data
from .drone import Drone
from .pathfinding import get_movement_cost, find_connection


class DroneScheduler:
    """Manages scheduling and movement of drones along a path."""

    def __init__(self, data: Data, path: list[str]) -> None:
        """
        Initialize the drone scheduler.

        Args:
            data: The drone network configuration
            path: The optimal path from start to end
        """
        self.data = data
        self.path = path
        self.drones: list[Drone] = []
        self.current_turn = 0
        self.next_drone_id = 0  # Track next drone to spawn
        self.total_drones_to_spawn = data.nb_drones

        # Limit drones to start hub capacity to prevent overflow
        start_hub_capacity = data.hubs[data.start_hub].max_drones
        initial_drones = min(data.nb_drones, start_hub_capacity)

        # Create initial drones up to start hub capacity
        for i in range(initial_drones):
            self.drones.append(
                Drone(
                    drone_id=i,
                    current_hub=path[0],
                    path_index=0,
                    turns_at_hub=0,
                    initial_stagger=0,
                )
            )
            self.next_drone_id = i + 1

    def get_hub_occupancy(self, hub_name: str) -> int:
        """Count how many active drones are currently at a hub."""
        return sum(
            1
            for d in self.drones
            if d.current_hub == hub_name and not d.completed
        )

    def get_connection_usage(self, hub_a: str, hub_b: str) -> int:
        """Count how many drones are currently traversing a connection."""
        # Simplified version - in reality would track drones in transit
        count = 0
        for d in self.drones:
            if not d.completed and d.path_index < len(self.path) - 1:
                if (
                    self.path[d.path_index] == hub_a
                    and self.path[d.path_index + 1] == hub_b
                ) or (
                    self.path[d.path_index] == hub_b
                    and self.path[d.path_index + 1] == hub_a
                ):
                    count += 1
        return count

    def can_move_drone(self, drone: Drone) -> bool:
        """Check if a drone can move to the next hub."""
        if drone.completed or drone.path_index >= len(self.path) - 1:
            return False

        current_hub = self.path[drone.path_index]
        next_hub = self.path[drone.path_index + 1]

        # Check if drone has waited enough turns for movement cost
        # (applies to current hub where drone is, not where it's going)
        movement_cost = get_movement_cost(current_hub, self.data)
        if drone.turns_at_hub < movement_cost:
            return False

        # Check hub capacity at next hub
        next_hub_obj = self.data.hubs[next_hub]
        if self.get_hub_occupancy(next_hub) >= next_hub_obj.max_drones:
            return False

        return True

    def validate_capacity_constraints(self) -> bool:
        """
        Validate that current state respects all capacity constraints.
        Returns True if valid, False if any constraint is violated.
        Raises ValueError with details if validation fails.
        """
        # Check hub capacities
        for hub_name, hub_obj in self.data.hubs.items():
            occupancy = self.get_hub_occupancy(hub_name)
            if occupancy > hub_obj.max_drones:
                drones_at_hub = [
                    d.drone_id
                    for d in self.drones
                    if d.current_hub == hub_name and not d.completed
                ]
                raise ValueError(
                    f"Hub '{hub_name}' capacity exceeded: "
                    f"{occupancy} drones (max: {hub_obj.max_drones}). "
                    f"Drones: {drones_at_hub}"
                )

        # Check connection capacities
        for conn in self.data.connections:
            usage = self.get_connection_usage(conn.hub_a, conn.hub_b)
            if usage > conn.max_link_capacity:
                raise ValueError(
                    f"Connection {conn.hub_a}-{conn.hub_b} capacity "
                    f"exceeded: {usage} drones "
                    f"(max: {conn.max_link_capacity})"
                )

        return True

    def advance_turn(self) -> None:
        """Advance simulation by one turn. Move drones individually.

        Moves drones one at a time in drone ID order (FIFO with priority),
        respecting capacity constraints. Prevents synchronized movement.
        """
        self.current_turn += 1

        # Increment turn counter for all drones at hubs
        for drone in self.drones:
            if not drone.completed:
                drone.turns_at_hub += 1

        # Collect candidates: drones that have waited long enough to move
        candidates = []
        for drone in self.drones:
            if drone.completed:
                continue

            if drone.path_index >= len(self.path) - 1:
                continue

            # Check if drone has waited enough for movement cost at current hub
            current_hub = self.path[drone.path_index]
            movement_cost = get_movement_cost(current_hub, self.data)
            if drone.turns_at_hub >= movement_cost:
                candidates.append(drone)

        # Sort candidates by drone ID for FIFO priority
        candidates.sort(key=lambda d: d.drone_id)

        # Track hub occupancy AFTER moves to check capacity
        # This counts: drones staying + drones entering (tracked as we go)
        hub_after_moves = {}
        for hub_name in self.data.hubs:
            # Count only drones staying at this hub (not moving away)
            hub_after_moves[hub_name] = sum(
                1
                for d in self.drones
                if d.current_hub == hub_name
                and not d.completed
                and d not in candidates
            )

        # Track how many drones are entering each hub

        drones_entering_hub = {}
        for hub_name in self.data.hubs:
            drones_entering_hub[hub_name] = 0

        # Track connection usage AFTER moves
        def get_connection_key(hub_a: str, hub_b: str) -> tuple[str, str]:
            """Normalize connection key (bidirectional)."""
            return tuple(sorted([hub_a, hub_b]))  # type: ignore

        connection_usage_after = {}
        for conn in self.data.connections:
            connection_usage_after[
                get_connection_key(conn.hub_a, conn.hub_b)
            ] = 0

        # Track how many drones have already moved OUT of each hub this turn
        drones_moved_from_hub = {}
        for hub_name in self.data.hubs:
            drones_moved_from_hub[hub_name] = 0

        # Move drones one at a time in priority order (by drone ID)
        drones_to_move = []
        for drone in candidates:
            current_hub = self.path[drone.path_index]
            next_hub = self.path[drone.path_index + 1]
            next_hub_obj = self.data.hubs[next_hub]

            # Restricted hubs limit outflow to 1 drone per turn
            movement_cost = get_movement_cost(current_hub, self.data)
            if movement_cost > 1 and drones_moved_from_hub[current_hub] > 0:
                continue  # Only 1 drone exits restricted hub per turn

            # Check hub capacity: staying drones + already entering drones
            # + this drone cannot exceed max_drones
            current_occupancy = (
                hub_after_moves[next_hub] + drones_entering_hub[next_hub]
            )
            if current_occupancy >= next_hub_obj.max_drones:
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
            drones_entering_hub[next_hub] += 1
            drones_moved_from_hub[current_hub] += 1
            if conn_key in connection_usage_after:
                connection_usage_after[conn_key] += 1

        # Move all approved drones simultaneously
        for drone in drones_to_move:
            drone.path_index += 1
            drone.current_hub = self.path[drone.path_index]
            # Reset wait counter (stagger applied via can_move_drone check)
            drone.turns_at_hub = 0

            # Check if drone reached the end
            if drone.path_index >= len(self.path) - 1:
                drone.completed = True

        # Validate capacity constraints after moves
        # Only validate hubs and connections that were actually used this turn
        try:
            # Check hub capacities
            for hub_name, hub_obj in self.data.hubs.items():
                occupancy = self.get_hub_occupancy(hub_name)
                if occupancy > hub_obj.max_drones:
                    drones_at_hub = [
                        d.drone_id
                        for d in self.drones
                        if d.current_hub == hub_name and not d.completed
                    ]
                    raise ValueError(
                        f"Hub '{hub_name}' capacity exceeded: "
                        f"{occupancy} drones (max: {hub_obj.max_drones}). "
                        f"Drones: {drones_at_hub}"
                    )

            # Check connection capacities - only for connections used by
            # drones that moved this turn
            for drone in drones_to_move:
                # Drone moved from its previous hub to current hub
                prev_hub = self.path[drone.path_index - 1]
                curr_hub = self.path[drone.path_index]

                # Count how many OTHER drones from drones_to_move also used
                # the same connection this turn
                connection_count = 1  # This drone
                for other in drones_to_move:
                    if other is drone:
                        continue
                    other_prev = self.path[other.path_index - 1]
                    other_curr = self.path[other.path_index]
                    same_connection = (
                        other_prev == prev_hub and other_curr == curr_hub
                    ) or (other_prev == curr_hub and other_curr == prev_hub)
                    if same_connection:
                        connection_count += 1

                conn = find_connection(prev_hub, curr_hub, self.data)
                if conn and connection_count > conn.max_link_capacity:
                    raise ValueError(
                        f"Connection {prev_hub}-{curr_hub} capacity "
                        f"exceeded: {connection_count} drones "
                        f"(max: {conn.max_link_capacity})"
                    )

        except ValueError as e:
            raise RuntimeError(str(e)) from e

        # Spawn new drones if capacity allows and we haven't spawned all yet
        self._spawn_new_drones()

    def _spawn_new_drones(self) -> None:
        """Spawn new drones at start hub if capacity allows."""
        if self.next_drone_id >= self.total_drones_to_spawn:
            return  # All drones already spawned

        start_hub_capacity = self.data.hubs[self.data.start_hub].max_drones

        # Spawn drones while capacity allows (recalculate each time)
        while self.next_drone_id < self.total_drones_to_spawn:
            # Recalculate occupancy to ensure we don't exceed capacity
            current_occupancy = self.get_hub_occupancy(self.data.start_hub)
            if current_occupancy >= start_hub_capacity:
                break  # Hub is at capacity, can't spawn more

            new_drone = Drone(
                drone_id=self.next_drone_id,
                current_hub=self.path[0],
                path_index=0,
                turns_at_hub=0,
                initial_stagger=0,
            )
            self.drones.append(new_drone)
            self.next_drone_id += 1

        # Verify start hub doesn't exceed capacity after spawning
        start_hub_occupancy = self.get_hub_occupancy(self.data.start_hub)
        if start_hub_occupancy > start_hub_capacity:
            raise RuntimeError(
                f"Start hub capacity exceeded: "
                f"{start_hub_occupancy} > {start_hub_capacity}"
            )

    def run_simulation(self, max_turns: int = 1000) -> dict:
        """
        Run the full simulation until all drones reach the end or max_turns.

        Args:
            max_turns: Maximum number of turns to simulate

        Returns:
            Dictionary with simulation results
        """
        while (
            self.current_turn < max_turns and not self.all_drones_completed()
        ):
            self.advance_turn()

        return {
            "total_turns": self.current_turn,
            "all_completed": self.all_drones_completed(),
            "drones": self.drones,
            "completion_times": self.get_completion_times(),
        }

    def all_drones_completed(self) -> bool:
        """Check if all drones have reached the end hub."""
        return all(d.completed for d in self.drones)

    def get_completion_times(self) -> dict[int, int]:
        """Get the turn at which each drone completed (if completed)."""
        times = {}
        for drone in self.drones:
            if drone.completed:
                # Approximate completion time (refined during simulation)
                times[drone.drone_id] = self.current_turn
        return times

    def get_drone_positions(self) -> dict[int, str]:
        """Get current hub position of each drone."""
        return {d.drone_id: self.path[d.path_index] for d in self.drones}
