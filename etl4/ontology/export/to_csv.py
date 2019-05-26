from typing import Iterable, Tuple, Dict

from etl4.ontology.export import Export

class ExportToCSV(Export):
    def __call__(self, composites: Iterable[Tuple[str, Dict]]):
        pass