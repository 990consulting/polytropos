from dataclasses import dataclass
from typing import List

import numpy

from polytropos.actions.evolve.__change import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId


@dataclass
class CalculateMeanProductivity(Change):
    annual_prod_var: VariableId
    mean_prod_var: VariableId

    def __call__(self, composite: Composite):
        periods: List[str] = list(composite.periods)
        annual_prods = [composite.get_observation(self.annual_prod_var, period) for period in periods]
        mean_prod = numpy.average(annual_prods)
        composite.put_immutable(self.mean_prod_var, mean_prod)
