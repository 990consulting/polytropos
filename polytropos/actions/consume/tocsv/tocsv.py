from typing import Iterable, Tuple, Any, Optional, List, Dict

from attr import dataclass

from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite

@dataclass
class ExportToCSV(Consume):
    filename: str
    descriptors: Dict   # Column descriptors, as specified in YAML -- processed in __post_init__

    def __post_init__(self) -> None:

        pass

    def before(self) -> None:
        pass

    def after(self) -> None:
        pass

    def extract(self, composite: Composite) -> Optional[Any]:
        pass

    def consume(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        pass