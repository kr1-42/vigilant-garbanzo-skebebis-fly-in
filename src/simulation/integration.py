"""Integration layer for drone movement tracking with scheduler."""

from ..algo import DroneScheduler, MultiPathDroneScheduler
from ..cls_data import Data
from .movement_tracker import DroneMovementTracker
from .output_formatter import SimulationOutputFormatter


class SimulationWithTracking:
    """Wraps DroneScheduler and tracks all drone movements for output."""

    def __init__(
        self, data: Data, path: list[str], enable_live_output: bool = True
    ):
        """
        Initialize the simulation with tracking.

        Args:
            data: The drone network data
            path: The optimal path for drones
            enable_live_output: Whether to print output to terminal
        """
        self.data = data
        self.path = path
        self.scheduler = DroneScheduler(data, path)
        self.tracker = DroneMovementTracker(path, data.nb_drones)
        self.formatter = SimulationOutputFormatter(self.tracker)
        self.enable_live_output = enable_live_output

        # Record initial positions
        for drone in self.scheduler.drones:
            self.tracker.drone_positions[drone.drone_id] = drone.path_index

    def advance_turn(self) -> None:
        """
        Advance the simulation by one turn and track movements.
        """
        # Record positions before movement
        positions_before = {
            drone.drone_id: drone.path_index for drone in self.scheduler.drones
        }

        # Advance scheduler
        self.scheduler.advance_turn()

        # Record all drone positions for this turn
        # This includes drones that didn't move (waiting at hubs)
        for drone in self.scheduler.drones:
            if drone.completed:
                continue

            old_pos = positions_before.get(drone.drone_id, drone.path_index)
            new_pos = drone.path_index

            # If drone moved, record the movement
            if new_pos > old_pos:
                self.tracker.record_movement(drone.drone_id, old_pos, new_pos)
            else:
                # Drone didn't move, but record its current position
                self.tracker.record_position(drone.drone_id, new_pos)

        # Print output for this turn if enabled
        if self.enable_live_output:
            self.formatter.print_turn_output(self.tracker.current_turn)

        # Advance tracker turn
        self.tracker.advance_turn()

    def all_drones_completed(self) -> bool:
        """Check if all drones have completed."""
        return self.scheduler.all_drones_completed()

    def get_hub_occupancy(self, hub_name: str) -> int:
        """Get number of drones at a hub."""
        return self.scheduler.get_hub_occupancy(hub_name)

    def get_tracker(self) -> DroneMovementTracker:
        """Get the movement tracker."""
        return self.tracker

    def get_formatter(self) -> SimulationOutputFormatter:
        """Get the output formatter."""
        return self.formatter

    @property
    def drones(self):
        """Get drones from scheduler."""
        return self.scheduler.drones

    @property
    def current_turn(self) -> int:
        """Get current turn from scheduler."""
        return self.scheduler.current_turn


class SimulationWithMultiPath:
    """Wraps MultiPathDroneScheduler and tracks all drone movements for out"""

    def __init__(
        self,
        data: Data,
        paths: list[list[str]],
        scheduler: MultiPathDroneScheduler,
        enable_live_output: bool = True,
    ):
        """
        Initialize multi-path simulation with tracking.

        Args:
            data: The drone network data
            paths: List of paths for drones
            scheduler: MultiPathDroneScheduler instance
            enable_live_output: Whether to print output to terminal  real-time
        """
        self.data = data
        self.paths = paths
        self.scheduler = scheduler
        self.primary_path = paths[0] if paths else []
        self.tracker = DroneMovementTracker(self.primary_path, data.nb_drones)
        self.formatter = SimulationOutputFormatter(self.tracker)
        self.enable_live_output = enable_live_output

        # Record initial positions
        for drone in self.scheduler.drones:
            self.tracker.drone_positions[drone.drone_id] = drone.path_index

    def advance_turn(self) -> None:
        """
        Advance the simulation by one turn and track movements.
        """
        # Record positions before movement
        positions_before = {
            drone.drone_id: drone.path_index for drone in self.scheduler.drones
        }

        # Advance scheduler
        self.scheduler.advance_turn()

        # Record movements - for multi-path, record actual hub positions
        for drone in self.scheduler.drones:
            if drone.completed:
                continue

            if drone.drone_id not in positions_before:
                # Newly spawned drone, record at current hub
                turn = self.tracker.current_turn
                if turn not in self.tracker.movement_history:
                    self.tracker.movement_history[turn] = []
                self.tracker.movement_history[turn].append(
                    (drone.drone_id, drone.current_hub)
                )
                self.tracker.drone_positions[drone.drone_id] = 0
            else:
                old_pos = positions_before[drone.drone_id]
                new_pos = drone.path_index

                # Record position (movement or stationary)
                turn = self.tracker.current_turn
                if turn not in self.tracker.movement_history:
                    self.tracker.movement_history[turn] = []

                # Add this drone's current position
                self.tracker.movement_history[turn].append(
                    (drone.drone_id, drone.current_hub)
                )
                self.tracker.drone_positions[drone.drone_id] = new_pos

                # Check if drone completed
                if new_pos > old_pos:
                    path_idx = self.scheduler.drone_path_assignment[
                        drone.drone_id
                    ]
                    drone_path = self.paths[path_idx]
                    if new_pos >= len(drone_path) - 1:
                        self.tracker.drone_completed.add(drone.drone_id)

        # Print output for this turn if enabled
        if self.enable_live_output:
            self.formatter.print_turn_output(self.tracker.current_turn)

        # Advance tracker turn
        self.tracker.advance_turn()

    def all_drones_completed(self) -> bool:
        """Check if all drones have completed."""
        return self.scheduler.all_drones_completed()

    def get_hub_occupancy(self, hub_name: str) -> int:
        """Get number of drones at a hub."""
        return self.scheduler.get_hub_occupancy(hub_name)

    def get_tracker(self) -> DroneMovementTracker:
        """Get the movement tracker."""
        return self.tracker

    def get_formatter(self) -> SimulationOutputFormatter:
        """Get the output formatter."""
        return self.formatter

    @property
    def drones(self):
        """Get drones from scheduler."""
        return self.scheduler.drones

    @property
    def current_turn(self) -> int:
        """Get current turn from scheduler."""
        return self.scheduler.current_turn
