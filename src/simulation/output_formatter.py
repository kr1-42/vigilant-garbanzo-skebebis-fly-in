"""Formats simulation output according to specification."""

from .movement_tracker import DroneMovementTracker


class SimulationOutputFormatter:
    """Formats and outputs simulation results in the required format."""

    def __init__(self, tracker: DroneMovementTracker):
        """
        Initialize the output formatter.

        Args:
            tracker: DroneMovementTracker instance with recorded movements
        """
        self.tracker = tracker

    def format_turn_output(self, turn: int) -> str:
        """
        Format the output for a single turn.

        Format: D<ID>-<destination> D<ID>-<destination> ...

        Args:
            turn: The turn number

        Returns:
            Formatted string for the turn, or empty string if no movements
        """
        movements = self.tracker.get_movements_for_turn(turn)

        if not movements:
            return ""

        # Sort by drone ID for consistent output
        movements_sorted = sorted(movements, key=lambda x: x[0])

        formatted_movements = [f"D{drone_id}-{destination}" for drone_id, destination in movements_sorted]
        return " ".join(formatted_movements)

    def print_turn_output(self, turn: int) -> None:
        """
        Print the output for a single turn to console.

        Args:
            turn: The turn number
        """
        turn_output = self.format_turn_output(turn)
        if turn_output:
            print(turn_output)

    def get_full_simulation_output(self) -> str:
        """
        Get the complete formatted simulation output.

        Returns:
            Multi-line string with one line per turn containing movements
        """
        output_lines = []

        # Find the highest turn number
        if not self.tracker.movement_history:
            return ""

        max_turn = max(self.tracker.movement_history.keys())

        # Format each turn's movements
        for turn in range(1, max_turn + 1):
            turn_output = self.format_turn_output(turn)
            if turn_output:  # Only include turns with movements
                output_lines.append(turn_output)

        return "\n".join(output_lines)

    def print_simulation_output(self) -> None:
        """Print the complete simulation output to console."""
        output = self.get_full_simulation_output()
        if output:
            print("\n=== SIMULATION OUTPUT ===")
            print(output)
            print("=== END SIMULATION ===\n")
        else:
            print("No drone movements recorded.")

    def save_to_file(self, filename: str) -> None:
        """
        Save the simulation output to a file.

        Args:
            filename: Path to the output file
        """
        output = self.get_full_simulation_output()

        if not output:
            print("No simulation output to save.")
            return

        try:
            with open(filename, 'w') as f:
                f.write(output)
            print(f"Simulation output saved to {filename}")
        except IOError as e:
            print(f"Error saving to {filename}: {e}")
