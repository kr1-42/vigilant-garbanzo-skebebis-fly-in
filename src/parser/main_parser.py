from sys import argv
from .dependency_check import check_dependencies
from ..cls_data import Data
from .file_parse import parse_file, parse_text


def main_parser() -> Data:
    """
    Main parser function to read configuration from a file.

    Returns a Data object with complete validation of the input file
    and raises descriptive errors on any issues.

    @returns: A Data object for the drone network configuration.
    @raises ValueError: If the input file is malformed or invalid.
    @raises ImportError: If required dependencies are missing.
    @raises FileNotFoundError: If the specified file does not exist.
    """
    if len(argv) != 2:
        raise ValueError("Usage: python fly_in.py <filename> or make")

    if check_dependencies() is False:
        raise ImportError(
            "Missing dependencies. Please install them ",
            "before running the program.",
        )

    filename: str = argv[1]

    # Validate file exists and is readable
    try:
        with open(filename, "r") as file:
            lines = parse_file(file)
            if not lines:
                raise ValueError(
                    "Configuration file is empty or contains only comments"
                )
            data: Data = parse_text(lines)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: '{filename}'")
    except IOError as e:
        raise IOError(f"Error reading configuration file '{filename}': {e}")
    except ValueError as e:
        error_msg = str(e)
        # Provide helpful context for common errors
        if "missing nb_drones" in error_msg:
            error_msg = (
                "Missing required field: nb_drones\n"
                "Add at the beginning: nb_drones: <number>"
            )
        elif "missing start_hub" in error_msg:
            error_msg = (
                "Missing required field: start_hub\n"
                "Example: start_hub: name 0 0"
            )
        elif "missing end_hub" in error_msg:
            error_msg = (
                "Missing required field: end_hub\nExample: end_hub: goal 10 10"
            )
        elif "multiple start_hub" in error_msg:
            error_msg = (
                "Error: multiple start_hub declarations\n"
                "Only one start_hub can be defined"
            )
        elif "undefined hub" in error_msg:
            error_msg = error_msg + "\nDefine it: hub: <name> <x> <y>"
        raise ValueError(error_msg)

    return data
