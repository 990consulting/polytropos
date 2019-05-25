from typing import Dict, Iterable, Any, Optional

from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.scan import Scan
from etl4.ontology.variable import Variable

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

    def scan(self, composite: Dict) -> Optional[Any]:
        pass

    def analyze(self, extracts: Iterable[Any]) -> None:
        pass

    def alter(self, composite: Dict) -> None:
        pass