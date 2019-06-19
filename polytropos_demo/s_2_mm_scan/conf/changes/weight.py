from dataclasses import dataclass
import scipy.stats
import numpy as np
from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.variable import Decimal


@dataclass
class AssignRegressionStats(Change):
    annual_weight_var: str = VariableValidator(data_type=Decimal, temporal=1)
    weight_slope_var: str = VariableValidator(data_type=Decimal, temporal=-1)
    weight_pval_var: str = VariableValidator(data_type=Decimal, temporal=-1)

    def __call__(self, composite: Composite):
        years = sorted([int(year) for year in composite.periods])
        weights = [composite.get_observation(self.annual_weight_var, str(year)) for year in years]
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(
            np.asarray(years), np.asarray(weights)
        )
        composite.put_immutable(self.weight_slope_var, slope)
        composite.put_immutable(self.weight_pval_var, p_value)
