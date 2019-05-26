from typing import Dict, Iterable, Tuple, Any, Optional

from etl4.ontology.scan import Scan

class AssignProductivityRank(Scan):
    def extract(self, composite: Dict) -> Optional[Any]:
        pass

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        pass

    def alter(self, composite_id: str, composite: Dict) -> None:
        pass