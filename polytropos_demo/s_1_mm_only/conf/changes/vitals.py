import logging
from dataclasses import dataclass

from polytropos.actions.evolve.__change import Change
from polytropos.actions.evolve.__lookup import lookup
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable, Decimal

@dataclass
class CalculateWeightGain(Change):
    """Determine the total weight gain over the observation period."""
    weight_var: str = VariableValidator(data_type=Decimal)
    weight_gain_var: str = VariableValidator(data_type=Decimal)

    def __call__(self, composite: Composite):
        logging.debug("Beginning CalculateWeightGain")
        periods = list(composite.periods)
        logging.debug("Observed the following periods: %s" % ", ".join(periods))
        earliest = min(periods)
        latest = max(periods)

        earliest_weight = composite.get_observation(self.weight_var, earliest)
        logging.debug("Earliest weight: %0.2f" % earliest_weight)

        latest_weight = composite.get_observation(self.weight_var, latest)
        logging.debug("Latest weight: %0.2f" % latest_weight)

        # I know, should have called it "weight change."
        weight_gain = round(latest_weight - earliest_weight, 2)
        logging.debug("Weight gain: %0.2f" % weight_gain)

        composite.put_immutable(self.weight_gain_var, weight_gain)
        logging.debug("Finished CalculateWeightGain.")

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
