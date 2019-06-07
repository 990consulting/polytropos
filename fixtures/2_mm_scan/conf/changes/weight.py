from dataclasses import dataclass
from typing import Dict

import scipy.stats
import numpy as np

from polytropos.ontology.metamorphosis import Change
from polytropos.ontology.metamorphosis.__subject import SubjectValidator
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable, Decimal
from polytropos.util import composites


@dataclass
class AssignRegressionStats(Change):
    annual_weight_var: Decimal = SubjectValidator(data_type=Decimal, temporal=1)
    weight_slope_var: Decimal = SubjectValidator(data_type=Decimal, temporal=-1)
    weight_pval_var: Decimal = SubjectValidator(data_type=Decimal, temporal=-1)

    def __call__(self, composite: Dict):
        years = sorted([int(year) for year in composites.get_periods(composite)])
        weights = [composites.get_observation(composite, str(year), self.annual_weight_var) for year in years]
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(
            np.asarray(years), np.asarray(weights)
        )
        composites.put_property(composite, self.weight_slope_var, slope)
        composites.put_property(composite, self.weight_pval_var, p_value)
