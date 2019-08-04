from dataclasses import field
from typing import Iterable, Tuple, Any, Optional, List, Dict

from attr import dataclass

from polytropos.actions.consume import Consume
from polytropos.actions.consume.tocsv.descriptor import ColumnDescriptor
from polytropos.ontology.composite import Composite

@dataclass
class ExportToCSV(Consume):
    columns: List[Dict]
    descriptor: ColumnDescriptor = field(init=False, default=None)

    def before(self):
        self.descriptor = ColumnDescriptor(self.schema, self.columns)
        pass

    def after(self):
        pass

    def extract(self, composite: Composite) -> Optional[Any]:
        pass

    def consume(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        pass