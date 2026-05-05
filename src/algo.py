import heapq
from dataclasses import dataclass
from .cls_data import Data


# Zone type movement costs (in turns)
ZONE_COSTS = {
    "normal": 1,
    "priority": 1,
    "restricted": 2,
    "blocked": float('inf'),  # Blocked zones are inaccessible
}


def get_movement_cost(hub_name: str, data: Data) -> int:
    """Get the movement cost (in turns) to enter a hub based on its zone type."""
    hub = data.hubs[hub_name]
    return ZONE_COSTS.get(hub.zone, 1)


def is_hub_accessible(hub_name: str, data: Data) -> bool:
    """Check if a hub is accessible (not blocked)."""
    hub = data.hubs[hub_name]
    return hub.zone != "blocked"


def find_connection(hub_a: str, hub_b: str, data: Data):
    """Find the connection between two hubs."""
    for conn in data.connections:
        if conn.contains(hub_a, hub_b):
            return conn
    return None


def dijkstra_find_path(data: Data) -> tuple[list[str], int] | None:
    """
    Find the optimal path from start_hub to end_hub using Dijkstra's algorithm.
    Accounts for zone movement costs, blocked zones, and capacity constraints.

    Args:
        data: The drone network data containing hubs, connections, and start/end hubs

    Returns:
        A tuple of (path, total_cost) where path is a list of hub names and
        total_cost is the total number of turns needed, or None if no path exists.

    Movement costs by zone type:
        - normal: 1 turn
        - priority: 1 turn (preferred)
        - restricted: 2 turns
        - blocked: inaccessible

    Constraints considered:
        - Blocked zones are skipped
        - Hub max_drones capacity is noted but path finding is optimistic
        - Connection max_link_capacity is noted but path finding is optimistic

    Example:
        result = dijkstra_find_path(data)
        if result:
            path, cost = result
            print(f"Path: {' -> '.join(path)}")
            print(f"Total turns: {cost}")
        else:
            print("No path found")
    """
    start = data.start_hub
    end = data.end_hub

    # Build adjacency list from valid connections
    graph: dict[str, list[str]] = {hub_name: [] for hub_name in data.hubs}

    for connection in data.connections:
        hub_a, hub_b = connection.hub_a, connection.hub_b

        # Only add edges if both hubs are accessible
        if is_hub_accessible(hub_a, data) and is_hub_accessible(hub_b, data):
            graph[hub_a].append(hub_b)
            graph[hub_b].append(hub_a)

    # Check if start and end are accessible
    if not is_hub_accessible(start, data) or not is_hub_accessible(end, data):
        return None

    # Dijkstra's algorithm
    # Priority queue: (cost, hub_name, path)
    pq = [(0, start, [start])]
    visited = set()
    distances = {hub: float('inf') for hub in data.hubs}
    distances[start] = 0

    while pq:
        cost, current_hub, path = heapq.heappop(pq)

        if current_hub in visited:
            continue

        visited.add(current_hub)

        # Found the end hub
        if current_hub == end:
            return path, cost

        # Explore neighbors
        for neighbor in graph[current_hub]:
            if neighbor not in visited:
                move_cost = get_movement_cost(neighbor, data)
                new_cost = cost + move_cost

                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    # No path found
    return None


def find_multiple_paths(data: Data, max_paths: int = 3) -> list[tuple[list[str], int]]:
    """
    Find multiple independent paths from start to end hub.
    Each path respects capacity constraints and zone accessibility.

    Args:
        data: The drone network data
        max_paths: Maximum number of paths to find

    Returns:
        List of (path, cost) tuples, sorted by cost (cheapest first)
    """
    paths = []
    excluded_edges = set()

    for _ in range(max_paths):
        # Build adjacency list, excluding edges used in previous paths
        graph: dict[str, list[str]] = {hub_name: [] for hub_name in data.hubs}

        for connection in data.connections:
            hub_a, hub_b = connection.hub_a, connection.hub_b
            edge = tuple(sorted([hub_a, hub_b]))

            # Only add edges that are accessible and not fully excluded
            if edge not in excluded_edges and \
               is_hub_accessible(hub_a, data) and is_hub_accessible(hub_b, data):
                graph[hub_a].append(hub_b)
                graph[hub_b].append(hub_a)

        start = data.start_hub
        end = data.end_hub

        # Check if start and end are still accessible
        if not is_hub_accessible(start, data) or not is_hub_accessible(end, data):
            break

        # Dijkstra's algorithm to find one path
        pq = [(0, start, [start])]
        visited = set()
        distances = {hub: float('inf') for hub in data.hubs}
        distances[start] = 0

        path_found = None
        while pq:
            cost, current_hub, path = heapq.heappop(pq)

            if current_hub in visited:
                continue

            visited.add(current_hub)

            if current_hub == end:
                path_found = (path, cost)
                break

            for neighbor in graph[current_hub]:
                if neighbor not in visited:
                    move_cost = get_movement_cost(neighbor, data)
                    new_cost = cost + move_cost

                    if new_cost < distances[neighbor]:
                        distances[neighbor] = new_cost
                        heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

        if path_found:
            paths.append(path_found)
            # Exclude edges used in this path for next iteration
            path, cost = path_found
            for i in range(len(path) - 1):
                edge = tuple(sorted([path[i], path[i + 1]]))
                excluded_edges.add(edge)
        else:
            break

    return paths if paths else []


def check_path_feasibility(path: list[str], data: Data) -> dict:
    """
    Check the feasibility of a given path considering capacity constraints.

    Args:
        path: List of hub names
        data: The drone network data

    Returns:
        Dictionary with feasibility information:
            - feasible: bool indicating if path is valid
            - hub_capacities: dict of hub max_drones
            - connection_capacities: dict of connection max_link_capacity
            - violations: list of any capacity constraint violations
    """
    violations = []
    hub_capacities = {}
    connection_capacities = {}

    # Check each hub in path
    for hub_name in path:
        if hub_name not in data.hubs:
            violations.append(f"Hub '{hub_name}' not found")
            continue

        hub = data.hubs[hub_name]
        hub_capacities[hub_name] = hub.max_drones

        if hub.zone == "blocked":
            violations.append(f"Hub '{hub_name}' is blocked and inaccessible")

    # Check each connection in path
    for i in range(len(path) - 1):
        hub_a, hub_b = path[i], path[i + 1]
        conn = find_connection(hub_a, hub_b, data)

        if conn is None:
            violations.append(f"No connection between '{hub_a}' and '{hub_b}'")
        else:
            connection_capacities[f"{hub_a}-{hub_b}"] = conn.max_link_capacity

    return {
        "feasible": len(violations) == 0,
        "hub_capacities": hub_capacities,
        "connection_capacities": connection_capacities,
        "violations": violations,
    }


@dataclass
class Drone:
    """Represents a single drone in the network."""
    drone_id: int
    current_hub: str  # Current location (hub name)
    path_index: int  # Index in the path where the drone is
    turns_at_hub: int  # Turns spent at current hub (waiting for movement cost)
    completed: bool = False  # True when drone reaches end hub

    def __repr__(self) -> str:
        return f"Drone({self.drone_id}, at={self.current_hub}, path_idx={self.path_index}, completed={self.completed})"


class DroneScheduler:
    """Manages scheduling and movement of multiple drones along an optimal path."""

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

        # Create all drones at the start hub
        for i in range(data.nb_drones):
            self.drones.append(Drone(
                drone_id=i,
                current_hub=data.start_hub,
                path_index=0,
                turns_at_hub=1,
            ))

    def get_hub_occupancy(self, hub_name: str) -> int:
        """Count how many active drones are currently at a hub."""
        return sum(1 for d in self.drones if d.current_hub == hub_name and not d.completed)

    def get_connection_usage(self, hub_a: str, hub_b: str) -> int:
        """Count how many drones are currently traversing a connection."""
        # This is a simplified version - in reality would track drones in transit
        count = 0
        for d in self.drones:
            if not d.completed and d.path_index < len(self.path) - 1:
                if (self.path[d.path_index] == hub_a and self.path[d.path_index + 1] == hub_b) or \
                   (self.path[d.path_index] == hub_b and self.path[d.path_index + 1] == hub_a):
                    count += 1
        return count

    def can_move_drone(self, drone: Drone) -> bool:
        """Check if a drone can move to the next hub."""
        if drone.completed or drone.path_index >= len(self.path) - 1:
            return False

        current_hub = self.path[drone.path_index]
        next_hub = self.path[drone.path_index + 1]

        # Check if drone has waited enough turns for movement cost
        movement_cost = get_movement_cost(next_hub, self.data)
        if drone.turns_at_hub < movement_cost:
            return False

        # Check hub capacity at next hub
        next_hub_obj = self.data.hubs[next_hub]
        if self.get_hub_occupancy(next_hub) >= next_hub_obj.max_drones:
            return False

        return True

    def advance_turn(self) -> None:
        """Advance simulation by one turn. Move drones if possible."""
        self.current_turn += 1

        # Increment turn counter for all drones at hubs
        for drone in self.drones:
            if not drone.completed:
                drone.turns_at_hub += 1

        # Try to move drones
        for drone in self.drones:
            if self.can_move_drone(drone):
                drone.path_index += 1
                drone.current_hub = self.path[drone.path_index]
                drone.turns_at_hub = 0

                # Check if drone reached the end
                if drone.path_index >= len(self.path) - 1:
                    drone.completed = True

    def run_simulation(self, max_turns: int = 1000) -> dict:
        """
        Run the full simulation until all drones reach the end or max_turns.

        Args:
            max_turns: Maximum number of turns to simulate

        Returns:
            Dictionary with simulation results
        """
        while self.current_turn < max_turns and not self.all_drones_completed():
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
        self.num_drones = data.nb_drones
        self.drones: list[Drone] = []
        self.drone_path_assignment: dict[int, int] = {}  # drone_id -> path_index
        self.current_turn = 0

        # Distribute drones across paths based on capacity
        self._distribute_drones_to_paths()

    def _distribute_drones_to_paths(self) -> None:
        """Distribute drones across paths, respecting capacity constraints."""
        drone_idx = 0

        for path_idx, path in enumerate(self.paths):
            # Calculate how many drones can use this path
            # Limited by the smallest hub capacity along the path
            min_hub_capacity = min(self.data.hubs[hub].max_drones for hub in path)
            drones_for_path = min(min_hub_capacity, self.num_drones - drone_idx)

            # Create drones for this path
            for i in range(drones_for_path):
                drone = Drone(
                    drone_id=drone_idx,
                    current_hub=self.data.start_hub,
                    path_index=0,
                    turns_at_hub=1,
                )
                self.drones.append(drone)
                self.drone_path_assignment[drone_idx] = path_idx
                drone_idx += 1

            if drone_idx >= self.num_drones:
                break

        # If not all drones could be assigned, add them to the best path
        if drone_idx < self.num_drones:
            best_path_idx = 0  # Use first path as fallback
            while drone_idx < self.num_drones:
                drone = Drone(
                    drone_id=drone_idx,
                    current_hub=self.data.start_hub,
                    path_index=0,
                    turns_at_hub=1,
                )
                self.drones.append(drone)
                self.drone_path_assignment[drone_idx] = best_path_idx
                drone_idx += 1

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

        current_hub = path[drone.path_index]
        next_hub = path[drone.path_index + 1]

        # Check if drone has waited enough turns for movement cost
        movement_cost = get_movement_cost(next_hub, self.data)
        if drone.turns_at_hub < movement_cost:
            return False

        # Check hub capacity at next hub (count drones going to this hub on same path)
        path_idx = self.drone_path_assignment[drone.drone_id]
        next_hub_occupancy = sum(
            1 for d in self.drones
            if not d.completed and
            self.drone_path_assignment[d.drone_id] == path_idx and
            path[d.path_index] == next_hub
        )

        next_hub_obj = self.data.hubs[next_hub]
        if next_hub_occupancy >= next_hub_obj.max_drones:
            return False

        return True

    def advance_turn(self) -> None:
        """Advance simulation by one turn. Move drones if possible."""
        self.current_turn += 1

        # Increment turn counter for all active drones
        for drone in self.drones:
            if not drone.completed:
                drone.turns_at_hub += 1

        # Try to move drones
        for drone in self.drones:
            if self.can_move_drone(drone):
                path = self.get_drone_path(drone)
                drone.path_index += 1
                drone.current_hub = path[drone.path_index]
                drone.turns_at_hub = 0

                # Check if drone reached the end
                if drone.path_index >= len(path) - 1:
                    drone.completed = True

    def all_drones_completed(self) -> bool:
        """Check if all drones have completed."""
        return all(d.completed for d in self.drones)

    def get_hub_occupancy(self, hub_name: str) -> int:
        """Count how many active drones are at a hub."""
        return sum(1 for d in self.drones if d.current_hub == hub_name and not d.completed)

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
