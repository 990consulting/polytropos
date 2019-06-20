from dataclasses import dataclass
from typing import Dict, Iterable, Any, Tuple

from polytropos.ontology.composite import Composite

from polytropos.actions.validator import VariableValidator
from polytropos.actions.scan import Scan
from polytropos.ontology.variable import Decimal, Integer


@dataclass
class AssignAverageBMIRank(Scan):
    mean_bmi_var: str = VariableValidator(data_type=Decimal, temporal=-1)
    bmi_rank_var: str = VariableValidator(data_type=Integer, temporal=-1)

    def __post_init__(self):
        self.ranked: Dict[str, int] = {}

    def extract(self, composite: Composite) -> float:
        mean_bmi = composite.get_immutable(self.mean_bmi_var)
        return mean_bmi

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        # Initialize data structure for analyzed data
        mean_bmi_dict: Dict[str, float] = {}

        for composite_id, mean_bmi in extracts:
            mean_bmi_dict[composite_id] = mean_bmi

        people_ranked = list(sorted(mean_bmi_dict.keys(), key=lambda k: -1 * mean_bmi_dict[k]))
        for k, person in enumerate(people_ranked):
            self.ranked[person] = k + 1

    def alter(self, composite_id: str, composite: Composite) -> None:
        rank = self.ranked[composite_id]
        composite.put_immutable(self.bmi_rank_var, rank)
