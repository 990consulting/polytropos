from typing import Dict, Iterable, Tuple, Any

from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.scan import Scan
from etl4.ontology.variable import Variable
from etl4.util import composites

class AssignProductivityRank(Scan):
    @subject("mean_prod_var", data_types={"Decimal"}, temporal=-1)
    @subject("prod_rank_var", data_type={"Integer"}, temporal=-1)
    def __init__(self, mean_prod_var, prod_rank_var):
        self.mean_prod_var: Variable = mean_prod_var
        self.prod_rank_var: Variable = prod_rank_var

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
