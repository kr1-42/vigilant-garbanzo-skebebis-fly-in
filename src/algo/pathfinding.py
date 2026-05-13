"""Pathfinding algorithms for drone routing through the network."""

import heapq
from ..cls_data import Data
from .constants import ZONE_COSTS


def get_movement_cost(hub_name: str, data: Data) -> int:
    """Get movement cost (turns) to enter a hub based on zone type."""
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
        data: The drone network data containing hubs, connections,
            and start/end hubs

    Returns:
        A tuple of (path, total_cost) where path is a list of hub names
        and total_cost is the total number of turns needed, or None if no
        path exists.

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
    distances = {hub: float("inf") for hub in data.hubs}
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


def find_multiple_paths(
    data: Data, max_paths: int = 3
) -> list[tuple[list[str], int]]:
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
            if (
                edge not in excluded_edges
                and is_hub_accessible(hub_a, data)
                and is_hub_accessible(hub_b, data)
            ):
                graph[hub_a].append(hub_b)
                graph[hub_b].append(hub_a)

        start = data.start_hub
        end = data.end_hub

        # Check if start and end are still accessible
        if not is_hub_accessible(start, data) or not is_hub_accessible(
            end, data
        ):
            break

        # Dijkstra's algorithm to find one path
        pq = [(0, start, [start])]
        visited = set()
        distances = {hub: float("inf") for hub in data.hubs}
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
                        heapq.heappush(
                            pq, (new_cost, neighbor, path + [neighbor])
                        )

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


def check_path_feasibility(
    path: list[str], data: Data, nb_drones: int = 0
) -> dict:
    """
    Check the feasibility of a given path considering capacity constraints.

    Args:
        path: List of hub names
        data: The drone network data
        nb_drones: Number of drones to route (optional, for capacity check)

    Returns:
        Dictionary with feasibility information:
            - feasible: bool indicating if path is valid
            - hub_capacities: dict of hub max_drones
            - connection_capacities: dict of connection max_link_capacity
            - min_hub_capacity: minimum hub capacity along the path
            - violations: list of any capacity constraint violations
    """
    violations = []
    hub_capacities = {}
    connection_capacities = {}
    min_hub_capacity = float("inf")

    # Check each hub in path
    for hub_name in path:
        if hub_name not in data.hubs:
            violations.append(f"Hub '{hub_name}' not found")
            continue

        hub = data.hubs[hub_name]
        hub_capacities[hub_name] = hub.max_drones
        min_hub_capacity = min(min_hub_capacity, hub.max_drones)

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

    # Check if path can accommodate all drones at start hub
    if nb_drones > 0:
        start_hub = data.hubs[path[0]]
        if nb_drones > start_hub.max_drones:
            violations.append(
                f"Start hub '{path[0]}' capacity ({start_hub.max_drones}) "
                f"cannot accommodate {nb_drones} drones"
            )

    if min_hub_capacity == float("inf"):
        min_hub_capacity = 0

    return {
        "feasible": len(violations) == 0,
        "hub_capacities": hub_capacities,
        "connection_capacities": connection_capacities,
        "min_hub_capacity": min_hub_capacity,
        "violations": violations,
    }
