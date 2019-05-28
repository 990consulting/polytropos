from typing import Dict, Iterable, Any, Tuple

from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.scan import Scan
from etl4.ontology.variable import Variable
from etl4.util import composites

class AssignAverageBMIRank(Scan):

    @subject("mean_bmi_var", data_types={"Decimal"}, temporal=-1)
    @subject("bmi_rank_var", data_type={"Integer"}, temporal=-1)
    def __init__(self, mean_bmi_var, bmi_rank_var):
        self.mean_bmi_var: Variable = mean_bmi_var
        self.bmi_rank_var: Variable = bmi_rank_var

        self.ranked: Dict[str, int] = {}

    def extract(self, composite: Dict) -> float:
        mean_bmi = composites.get_property(composite, self.mean_bmi_var)
        return mean_bmi

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        # Initialize data structure for analyzed data
        mean_bmi_dict: Dict[str, float] = {}

        for composite_id, mean_bmi in extracts:
            mean_bmi_dict[composite_id] = mean_bmi

        people_ranked = list(sorted(mean_bmi_dict.keys(), key=lambda k: -1 * mean_bmi_dict[k]))
        for k, person in enumerate(people_ranked):
            self.ranked[person] = k + 1

    def alter(self, composite_id: str, composite: Dict) -> None:
        rank = self.ranked[composite_id]
        composites.put_property(composite, self.bmi_rank_var, rank)
