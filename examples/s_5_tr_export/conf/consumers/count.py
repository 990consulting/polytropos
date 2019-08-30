from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, Any
import os

from polytropos.actions.consume import Consume

@dataclass
class Count(Consume):
    filename: str

    def __post_init__(self):
        self.n = 0

    def before(self):
        pass

    def consume(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        for _ in extracts:
            self.n += 1

    def extract(self, composite: Dict):
        return True

    def after(self):
        filename = os.path.join(self.path_locator.conf_dir, '../', self.filename)
        filepath = os.path.dirname(filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(filename, "w") as fh:
            fh.write("I saw %i composites" % self.n)
