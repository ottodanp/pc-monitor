from os import mkdir
from os.path import isdir


def make_directory(path: str) -> None:
    if not isdir(path):
        mkdir(path)
