from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, Any

from polytropos.actions.evolve import SubjectValidator
from polytropos.actions.scan import Scan
from polytropos.ontology.variable import Decimal, Integer
from polytropos.util import composites


@dataclass
class AssignProductivityRank(Scan):
    mean_prod_var: Decimal = SubjectValidator(data_type=Decimal, temporal=-1)
    prod_rank_var: Integer = SubjectValidator(data_type=Integer, temporal=-1)

    def __post_init__(self):
        self.ranked: Dict[str, int] = {}

    def extract(self, composite: Dict) -> float:
        mean_prod = composites.get_property(composite, self.mean_prod_var)
        return mean_prod

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        # Initialize data structure for analyzed data
        mean_prod_dict: Dict[str, float] = {}
        for composite_id, mean_prod in extracts:
            mean_prod_dict[composite_id] = mean_prod

        cities_ranked = list(sorted(mean_prod_dict.keys(), key=lambda k: -1 * mean_prod_dict[k]))
        for k, city in enumerate(cities_ranked):
            self.ranked[city] = k + 1

    def alter(self, composite_id: str, composite: Dict) -> None:
        rank = self.ranked[composite_id]
        composites.put_property(composite, self.prod_rank_var, rank)
