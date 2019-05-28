from typing import Dict

import scipy.stats

from etl4.ontology.metamorphosis import Change
from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.schema import Schema
from etl4.ontology.variable import Variable
from etl4.util import composites

class AssignRegressionStats(Change):
    @subject("annual_weight_var", data_types={"Decimal"}, temporal=1)
    @subject("weight_slope_var", data_types={"Decimal"}, temporal=-1)
    @subject("weight_pval_var", data_types={"Decimal"}, temporal=-1)
    def __init__(self, schema: Schema, lookups: Dict, annual_weight_var, weight_slope_var, weight_pval_var):
        super().__init__(schema, lookups, annual_weight_var, weight_slope_var, weight_pval_var)
        self.annual_weight_var: Variable = annual_weight_var
        self.weight_slope_var = weight_slope_var
        self.weight_pval_var = weight_pval_var

    def __call__(self, composite: Dict):
        years = sorted([int(year) for year in composites.get_periods(composite)])
        weights = (composites.get_observation(composite, str(year), self.annual_weight_var) for year in years)
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(years, weights)
        composites.put_property(composite, self.weight_slope_var, slope)
        composites.put_property(composite, self.weight_pval_var, slope)
