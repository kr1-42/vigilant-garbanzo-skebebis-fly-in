"""Functions for estimating turn requirements for drone routing strategies."""

from ..cls_data import Data
from .pathfinding import get_movement_cost


def estimate_single_path_turns(
    path: list[str], nb_drones: int, data: Data
) -> int:
    """
    Estimate total turns needed for all drones on a single path.
    Accounts for movement costs and basic capacity constraints.

    Args:
        path: The path as a list of hub names
        nb_drones: Number of drones to send
        data: The drone network data

    Returns:
        Estimated total turns needed
    """
    if not path or len(path) < 2:
        return 0

    # Calculate path cost (sum of movement costs)
    total_path_cost = 0
    for hub_name in path[1:]:  # Skip start hub
        total_path_cost += get_movement_cost(hub_name, data)

    # Estimate turns based on capacity constraints
    # If all drones fit on the path at once (simplified), they move in parallel
    # Otherwise, they queue and move sequentially
    min_hub_capacity = min((data.hubs[h].max_drones for h in path), default=1)

    if nb_drones <= min_hub_capacity:
        # All drones can move in parallel
        return total_path_cost
    else:
        # Drones need to queue up
        # Rough estimate: sequential offset
        return total_path_cost + (nb_drones - 1) * 1


def estimate_multiple_paths_turns(
    paths: list[tuple[list[str], int]], nb_drones: int
) -> int:
    """
    Estimate total turns needed for multiple disjoint paths.
    Assumes drones are distributed across paths and move in parallel.

    Args:
        paths: List of (path, cost) tuples
        nb_drones: Number of drones to send

    Returns:
        Estimated total turns needed (max path cost among distributed drones)
    """
    if not paths:
        return 9999

    # Sort paths by cost (most expensive first)
    sorted_paths = sorted(paths, key=lambda p: p[1], reverse=True)

    # Distribute drones round-robin across paths
    drones_per_path = [0] * len(sorted_paths)
    for i in range(nb_drones):
        drones_per_path[i % len(sorted_paths)] += 1

    # Total turns is the cost of the most expensive path
    # (since drones move in parallel on different paths)
    max_turns = 0
    for path_idx, (path, cost) in enumerate(sorted_paths):
        # Simple estimate: just use path cost
        max_turns = max(max_turns, cost)

    return max_turns
