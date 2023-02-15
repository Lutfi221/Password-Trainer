import logging
import base64
import json
import os
from typing import Optional


l = logging.getLogger(__name__)


def base64_str_to_bytes(s: str):
    return base64.decodebytes(s.encode("ascii"))


def bytes_to_base64_str(data: bytes):
    return base64.encodebytes(data).decode("ascii")


class InvalidJsonFileError(Exception):
    path: str
    lineno: int
    colno: int

    def __init__(self, path: str, lineno: int, colno: int):
        super().__init__(
            "Invalid JSON at `{}` line {} column {}".format(path, lineno, colno)
        )
        self.path = path
        self.lineno = lineno
        self.colno = colno


def read_json_file(path: str, default: Optional[any] = None) -> any:
    l.info("Reading json file from {}".format(path))
    if os.stat(path).st_size == 0:
        l.info("JSON file is empty, returning default object")
        return default
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError as e:
        raise InvalidJsonFileError(path, e.lineno, e.colno)
    return data


def write_json_to_file(path: str, data: any):
    l.info("Writing json into file at {}".format(path))
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return data
