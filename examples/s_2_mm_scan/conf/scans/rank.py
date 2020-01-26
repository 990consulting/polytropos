from dataclasses import dataclass
from typing import Dict, Iterable, Any, Tuple

from polytropos.actions.scan import Scan
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId


@dataclass
class AssignAverageBMIRank(Scan):
    male_flag: VariableId
    mean_bmi_var: VariableId
    bmi_rank_gender_var: VariableId
    bmi_rank_overall_var: VariableId

    def __post_init__(self):
        self.ranked: Dict[str, Dict[str, int]] = {}

    def extract(self, composite: Composite) -> Tuple[bool, float]:
        mean_bmi = composite.get_immutable(self.mean_bmi_var)
        is_male = composite.get_immutable(self.male_flag)
        return is_male, mean_bmi

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        # Initialize data structure for analyzed data
        mean_bmi_dict: Dict[str, Dict[str, float]] = {}
        genders = ["male", "female", "overall"]
        for gender in genders:
            mean_bmi_dict[gender] = {}
            self.ranked[gender] = {}

        for composite_id, (is_male, mean_bmi) in extracts:
            if is_male:
                gender: str = "male"
            else:
                gender = "female"
            mean_bmi_dict[gender][composite_id] = mean_bmi
            mean_bmi_dict["overall"][composite_id] = mean_bmi

        for gender in genders:
            people_ranked = list(sorted(mean_bmi_dict[gender].keys(), key=lambda k: -1 * mean_bmi_dict[gender][k]))
            for k, person in enumerate(people_ranked):
                self.ranked[gender][person] = k + 1

    def _get_gender(self, composite_id: str) -> str:
        if composite_id in self.ranked["male"]:
            return "male"
        return "female"

    def alter(self, composite_id: str, composite: Composite) -> None:
        overall_rank = self.ranked["overall"][composite_id]
        composite.put_immutable(self.bmi_rank_overall_var, overall_rank)

        gender: str = self._get_gender(composite_id)
        gender_rank = self.ranked[gender][composite_id]
        composite.put_immutable(self.bmi_rank_gender_var, gender_rank)
