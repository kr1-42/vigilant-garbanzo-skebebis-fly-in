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
    data: Data = main_parser()
    visualize(data)
    return 0



if __name__ == "__main__":
    sys.exit(fly_in())
