from src.parser.main_parser import main_parser
from src.cls_data import Data
from src.visualizer import visualize


def fly_in():
    data: Data = main_parser()
    visualize(data)


if __name__ == "__main__":
    fly_in()
