from dataclasses import dataclass
from typing import Dict
import os

from polytropos.actions.consume import Consume

@dataclass
class Count(Consume):
    filename: str

    def __post_init__(self):
        self.n = 0

    def consume(self, composite_id: str, composite: Dict):
        self.n += 1

    def after(self):
        filename = os.path.join(self.output_dir, self.filename)
        filepath = os.path.dirname(filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(filename, "w") as fh:
            fh.write("I saw %i composites" % self.n)
