from dataclasses import dataclass
from typing import Dict

from polytropos.actions.evolve.__change import Change
from polytropos.actions.evolve.__lookup import lookup
from polytropos.actions.evolve.__subject import SubjectValidator
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable, Decimal

@dataclass
class CalculateWeightGain(Change):
    """Determine the total weight gain over the observation period."""
    weight_var: Decimal = SubjectValidator(data_type=Decimal)
    weight_gain_var: Decimal = SubjectValidator(data_type=Decimal)

    def __call__(self, composite: Composite):
        periods = composite.periods
        earliest = min(periods)
        latest = max(periods)

        earliest_weight = composite.get_observation(self.weight_var.var_id, earliest)
        latest_weight = composite.get_observation(self.weight_var.var_id, latest)

        # I know, should have called it "weight change."
        weight_gain = round(latest_weight - earliest_weight, 2)

        composite.put_immutable(self.weight_gain_var.var_id, weight_gain)

@lookup('genders')
@dataclass
class DetermineGender(Change):
    """Use a lookup table to determine the person's gender."""
    person_name_var: Variable
    gender_var: Variable

    # @lookup("genders")

    def __call__(self, composite: Composite):
        person_name: str = composite.get_immutable(self.person_name_var.var_id)
        lc_name = person_name.lower()

        gender = self.lookups["genders"][lc_name]
        composite.put_immutable(self.gender_var.var_id, gender)
