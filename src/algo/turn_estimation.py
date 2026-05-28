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
    Accounts for shared bottleneck hubs between paths.

    Args:
        paths: List of (path, cost) tuples
        nb_drones: Number of drones to send

    Returns:
        Estimated total turns needed, accounting for bottlenecks
    """
    if not paths:
        return 9999

    if len(paths) == 0:
        return 9999

    # Find shared (convergence) hubs between paths
    all_hubs_per_path = [set(path) for path, _ in paths]

    # Check if paths share hubs (excluding start and end)
    shared_hubs = None
    if len(all_hubs_per_path) > 1:
        shared_hubs = set.intersection(*all_hubs_per_path)
        if shared_hubs:
            # Remove start and end from shared analysis
            shared_hubs.discard(paths[0][0][0])  # start
            shared_hubs.discard(paths[0][0][-1])  # end

    # If paths share intermediate hubs, they have a bottleneck
    if shared_hubs:
        # Paths are NOT truly independent
        # Calculate with bottleneck factor
        max_path_cost = max(cost for _, cost in paths)

        # Number of shared paths through convergence point
        num_paths_sharing = len(paths)

        # Estimate queuing: if paths share hubs, drones must queue
        # Each wave of drones = (nb_drones / num_paths) per path
        drones_per_path = nb_drones / num_paths_sharing

        # Queuing overhead: extra turns from drones exceeding capacity
        queuing_overhead = max(0, (drones_per_path - 1) * num_paths_sharing)

        return max_path_cost + int(queuing_overhead)
    else:
        # Paths are truly independent
        # Total turns is the most expensive path (parallelism benefit)
        max_turns = max(cost for _, cost in paths)
        return max_turns
