from dataclasses import dataclass
from typing import Dict, List
from polytropos.actions.consume import Consume

@dataclass
class ExportToCSV(Consume):
    filename: str     # The name of the file to which to write the data.
    invariant: bool   # Is this an export for temporal or invariant data? (Can't mix)
    columns: List     #

    def consume(self, composite_id: str, composite: Dict):
        pass