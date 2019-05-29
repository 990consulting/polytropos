from dataclasses import dataclass
from typing import Dict, Iterable, Any, Tuple

from etl4.ontology.metamorphosis.__subject import SubjectValidator
from etl4.ontology.scan import Scan
from etl4.ontology.variable import Variable, Binary, Decimal, Integer
from etl4.util import composites


@dataclass
class AssignAverageBMIRank(Scan):
    male_flag: Binary = SubjectValidator(data_type=Binary, temporal=-1)
    mean_bmi_var: Decimal = SubjectValidator(data_type=Decimal, temporal=-1)
    bmi_rank_gender_var: Integer = SubjectValidator(data_type=Integer, temporal=-1)
    bmi_rank_overall_var: Integer = SubjectValidator(data_type=Integer, temporal=-1)

    def __post_init(self):
        self.ranked: Dict[str, Dict[str, int]] = {}

    def extract(self, composite: Dict) -> Tuple[bool, float]:
        mean_bmi = composites.get_property(composite, self.mean_bmi_var)
        is_male = composites.get_property(composite, self.male_flag)
        return is_male, mean_bmi

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        # Initialize data structure for analyzed data
        mean_bmi_dict: Dict[str, Dict[str, float]] = {}
        genders = ["male", "female", "overall"]
        for gender in genders:
            mean_bmi_dict[gender] = {}

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

    def alter(self, composite_id: str, composite: Dict) -> None:
        overall_rank = self.ranked["overall"][composite_id]
        composites.put_property(composite, self.bmi_rank_overall_var, overall_rank)

        gender: str = self._get_gender(composite_id)
        gender_rank = self.ranked[gender][composite_id]
        composites.put_property(composite, self.bmi_rank_gender_var, gender_rank)
