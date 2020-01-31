from dataclasses import dataclass

import numpy as np
import scipy.stats

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId


@dataclass
class AssignRegressionStats(Change):
    annual_weight_var: VariableId
    weight_slope_var: VariableId
    weight_pval_var: VariableId

    def __call__(self, composite: Composite):
        years = sorted([int(year) for year in composite.periods])
        weights = [composite.get_observation(self.annual_weight_var, str(year)) for year in years]
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(
            np.asarray(years), np.asarray(weights)
        )
        composite.put_immutable(self.weight_slope_var, slope)
        composite.put_immutable(self.weight_pval_var, p_value)
