from sys import argv
from .dependency_check import check_dependencies
from ..cls_data import Data
from .file_parse import parse_file, parse_text


def main_parser() -> Data:
    """
    Main parser function to read configuration from a file and return a Data object.

    Performs complete validation of the input file and raises descriptive errors
    on any issues.

    @returns: A Data object containing the parsed configuration for the drone network.
    @raises ValueError: If the input file is malformed or contains invalid data.
    @raises ImportError: If required dependencies are missing.
    @raises FileNotFoundError: If the specified input file does not exist.
    """
    if len(argv) != 2:
        raise ValueError("Usage: python fly_in.py <filename> or make")

    if check_dependencies() == False:
        raise ImportError("Missing dependencies. Please install them before running the program.")

    filename: str = argv[1]

    # Validate file exists and is readable
    try:
        with open(filename, 'r') as file:
            lines = parse_file(file)
            if not lines:
                raise ValueError("Configuration file is empty or contains only comments")
            data: Data = parse_text(lines)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: '{filename}'")
    except IOError as e:
        raise IOError(f"Error reading configuration file '{filename}': {e}")

    return data

