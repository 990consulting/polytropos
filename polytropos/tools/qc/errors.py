from typing import Iterable

from polytropos.util.nesteddicts import path_to_str

class UnrecognizedVariablePathError(ValueError):
    def __init__(self, path: Iterable[str]):
        self.path = tuple(path)

    def __str__(self) -> str:
        msg: str = "Unrecognized variable %s" % path_to_str(self.path)
        return msg