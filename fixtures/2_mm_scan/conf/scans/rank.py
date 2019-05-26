from typing import Dict, Iterable, Any, Tuple

from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.scan import Scan
from etl4.ontology.variable import Variable
from etl4.util import composites

class AssignAverageBMIRank(Scan):

    @subject("male_flag", data_types={"Binary"}, temporal=-1)
    @subject("mean_bmi_var", data_types={"Decimal"}, temporal=-1)
    @subject("bmi_rank_gender_var", data_type={"Decimal"}, temporal=-1)
    @subject("bmi_rank_overall_var", data_type={"Decimal"}, temporal=-1)
    def __init__(self, male_flag, mean_bmi_var, bmi_rank_gender_var, bmi_rank_overall_var):
        self.male_flag: Variable = male_flag
        self.mean_bmi_var: Variable = mean_bmi_var
        self.bmi_rank_gender_var: Variable = bmi_rank_gender_var
        self.bmi_rank_overall_var: Variable = bmi_rank_overall_var

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
