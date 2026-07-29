"""Path optimization strategies for drone routing."""

from ..cls_data import Data
from .pathfinding import dijkstra_find_path, find_multiple_paths
from .turn_estimation import (
    estimate_single_path_turns,
    estimate_multiple_paths_turns,
)


def optimize_path_strategy(
    data: Data,
) -> tuple[list[list[str]] | list[str], str]:
    """
    Optimize the pathfinding strategy by comparing single vs. multiple paths.
    Chooses the approach that minimizes total turns for all drones.

    Args:
        data: The drone network data

    Returns:
        Tuple of (paths, strategy_used) where:
        - paths is either a list of paths (for multiple) or a single path
        - strategy_used is either "multiple" or "single"
    """
    # Try to find a single optimal path
    single_path_result = dijkstra_find_path(data)
    single_path = None
    single_path_cost = float("inf")

    if single_path_result:
        single_path, single_path_cost = single_path_result

    # Try to find multiple paths
    multiple_paths = find_multiple_paths(
        data, max_paths=min(data.nb_drones, 3)
    )

    # Compare strategies
    use_multiple = False
    best_paths: list[list[str]] | list[str]
    if single_path:
        best_paths = single_path
    else:
        best_paths = []

    if multiple_paths and single_path:
        # Both strategies exist - compare total turns
        single_turns = estimate_single_path_turns(
            single_path, data.nb_drones, data
        )
        multiple_turns = estimate_multiple_paths_turns(
            multiple_paths, data.nb_drones
        )

        if multiple_turns < single_turns:
            use_multiple = True
            best_paths = [p[0] for p in multiple_paths]
        else:
            use_multiple = False
    elif multiple_paths and not single_path:
        # Only multiple paths exist
        use_multiple = True
        best_paths = [path for path, _ in multiple_paths]

        print("Only multiple paths found (single path not feasible)")

    strategy = "multiple" if use_multiple else "single"
    return best_paths, strategy
