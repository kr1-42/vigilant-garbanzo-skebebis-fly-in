from sys import argv
from .dependency_check import check_dependencies
from ..cls_data import Data
from .file_parse import parse_file, parse_text


def main_parser() -> Data:
    """ Main parser function to read configuration from a file and return a Data object.
    @returns: A Data object containing the parsed configuration for the drone network.
    @raises ValueError: If the input file is malformed or contains invalid data.
    @raises ImportError: If required dependencies are missing.
    @raises FileNotFoundError: If the specified input file does not exist. """
    if len(argv) != 2:
        raise ValueError("Usage: python fly_on.py <filename> or make")
    if check_dependencies() == False:
        raise ImportError("Missing dependencies. Please install them before running the program.")
    filename: str = argv[1]
    try:
        with open(filename, 'r') as file:
            data: Data = parse_text(parse_file(file))
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{filename}' not found.")
    return data

