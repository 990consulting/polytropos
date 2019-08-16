from typing import Iterable, Tuple, Any, Optional, List, Dict

from attr import dataclass

from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite

@dataclass
class ExportToCSV(Consume):
    columns: List[Dict]

    def before(self):
        pass

    def after(self):
        pass

    def extract(self, composite: Composite) -> Optional[Any]:
        pass

    def consume(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        pass