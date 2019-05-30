from dataclasses import dataclass, Field
from typing import Dict

from etl4.ontology.consume import Consume

@dataclass
class Count(Consume):
    filename: str

    def __init__(self):
        self.n = 0

    def consume(self, composite_id: str, composite: Dict):
        self.n += 1

    def after(self):
        with open(self.filename, "w") as fh:
            fh.write("I saw %i composites" % self.n)
