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
        visualize(data)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except ImportError as e:
        print(f"Dependency Error: {e}", file=sys.stderr)
        return 4
    except KeyboardInterrupt:
        print("\nProgram interrupted by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(fly_in())
