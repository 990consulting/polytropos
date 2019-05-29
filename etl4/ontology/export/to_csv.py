from typing import Iterable, Tuple, Dict
from etl4.ontology.consume import Consume

class ExportToCSV(Consume):
    def __call__(self, composites: Iterable[Tuple[str, Dict]]):
        pass