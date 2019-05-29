from dataclasses import dataclass
from typing import Dict, Iterable, List

import numpy

from etl4.ontology.metamorphosis import Change
from etl4.ontology.variable import Variable
from etl4.util import composites


@dataclass
class CalculateMeanProductivity(Change):
    # TODO: Validation
    annual_prod_var: Variable
    mean_prod_var: Variable

    def __call__(self, composite: Dict):
        periods: List[str] = list(composites.get_periods(composite))
        annual_prods = (composites.get_observation(composite, period, self.annual_prod_var) for period in periods)
        mean_prod = numpy.average(annual_prods)
        composites.put_property(composite, self.mean_prod_var, mean_prod)
