from dataclasses import dataclass
from typing import Dict

from polytropos.ontology.metamorphosis.__change import Change
from polytropos.ontology.metamorphosis.__lookup import lookup
from polytropos.ontology.metamorphosis.__subject import SubjectValidator
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable, Decimal
from polytropos.util import nesteddicts

@dataclass
class CalculateWeightGain(Change):
    """Determine the total weight gain over the observation period."""
    weight_var: Decimal = SubjectValidator(data_type=Decimal)
    weight_gain_var: Decimal = SubjectValidator(data_type=Decimal)

    def __call__(self, composite: Dict):
        periods = set(composite.keys()) - {"invariant"}
        earliest = min(periods)
        latest = max(periods)

        weight_path = list(self.weight_var.absolute_path)

        earliest_weight_path: list = [earliest] + weight_path
        earliest_weight: float = nesteddicts.get(composite, earliest_weight_path)

        latest_weight_path: list = [latest] + weight_path
        latest_weight: float = nesteddicts.get(composite, latest_weight_path)

        # I know, should have called it "weight change."
        weight_gain = round(latest_weight - earliest_weight, 2)

        weight_gain_path = ["invariant"] + list(self.weight_gain_var.absolute_path)
        nesteddicts.put(composite, weight_gain_path, weight_gain)

@lookup('genders')
@dataclass
class DetermineGender(Change):
    """Use a lookup table to determine the person's gender."""
    person_name_var: Variable
    gender_var: Variable

    # @lookup("genders")

    def __call__(self, composite: Dict):
        person_name_path = ["invariant"] + list(self.person_name_var.absolute_path)
        person_name: str = nesteddicts.get(composite, person_name_path)
        lc_name = person_name.lower()

        gender = self.lookups["genders"][lc_name]
        gender_path = ["invariant"] + list(self.gender_var.absolute_path)
        nesteddicts.put(composite, gender_path, gender)
