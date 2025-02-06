from hashlib import sha256
from os import mkdir
from os.path import isdir, isfile
from random import choice

CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_auth_code() -> str:
    return "".join(choice(CHARSET) for _ in range(6))


def make_directory(path: str) -> None:
    if not isdir(path):
        mkdir(path)


def get_latest_image_hash(path: str) -> str:
    if not isfile(path):
        return ""

    with open(path, "rb") as f:
        data = f.read()

    return sha256(data).hexdigest()
