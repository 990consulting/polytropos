from dataclasses import dataclass, Field
from typing import Dict
import os

from polytropos.ontology.consume import Consume

@dataclass
class Count(Consume):
    filename: str

    def __post_init__(self):
        self.n = 0

    def consume(self, composite_id: str, composite: Dict):
        self.n += 1

    def after(self):
        filename = os.path.join(self.path_locator.conf_dir, '../', self.filename)
        with open(filename, "w") as fh:
            fh.write("I saw %i composites" % self.n)
