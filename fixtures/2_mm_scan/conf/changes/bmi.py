from typing import Dict

from etl4.ontology.metamorphosis import Change
from etl4.ontology.metamorphosis.__subject import subject
from etl4.ontology.schema import Schema
from etl4.ontology.variable import Variable
from etl4.util import composites
import numpy

class AssignAnnualBMI(Change):
    @subject("annual_weight_var", data_types={"Decimal"}, temporal=1)
    @subject("height_var", data_types={"Decimal", "Integer"}, temporal=-1)
    @subject("annual_bmi_var", data_types={"Decimal"}, temporal=1)
    def __init__(self, schema: Schema, lookups: Dict, annual_weight_var, height_var, annual_bmi_var):
        super().__init__(schema, lookups, annual_weight_var, height_var, annual_bmi_var)
        self.annual_weight_var: Variable = annual_weight_var
        self.height_var: Variable = height_var
        self.annual_bmi_var: Variable = annual_bmi_var

    def __call__(self, composite: Dict):
        h_squared = composites.get_property(composite, self.height_var) ** 2
        for period, weight in composites.get_all_observations(composite, self.annual_weight_var):
            bmi = weight / h_squared * 703
            composites.put_observation(composite, period, self.annual_bmi_var, bmi)

class AssignMeanBMI(Change):
    @subject("annual_bmi_var", data_types={"Decimal"}, temporal=1)
    @subject("mean_bmi_var", data_types={"Decimal"}, temporal=-1)
    def __init__(self, schema: Schema, lookups: Dict, annual_bmi_var, mean_bmi_var):
        super().__init__(schema, lookups, annual_bmi_var, mean_bmi_var)
        self.annual_bmi_var: Variable = annual_bmi_var
        self.mean_bmi_var: Variable = mean_bmi_var

    def __call__(self, composite: Dict):
        bmis = (bmi for period, bmi in composites.get_all_observations(composite, self.annual_bmi_var))
        mean_bmi = numpy.average(bmis)
        composites.put_property(composite, self.mean_bmi_var, mean_bmi)
