import sys
from src.parser.main_parser import main_parser
from src.cls_data import Data
from src.visualizer import visualize


def fly_in() -> int:
    """
    Main entry point for the drone network visualization.

    Exit codes:
        0 - Success
        1 - Configuration/validation error
        2 - File not found
        3 - Runtime error during visualization
        4 - Dependency error
    """
    try:
        data: Data = main_parser()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 4
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1

    try:
        visualize(data)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        return 0
    except Exception as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(fly_in())
