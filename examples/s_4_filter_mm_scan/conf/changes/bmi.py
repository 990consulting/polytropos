from dataclasses import dataclass
from typing import Dict
import numpy
from polytropos.ontology.composite import Composite

from polytropos.actions.evolve.__change import Change
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.variable import Decimal, Integer, Primitive


@dataclass
class AssignAnnualBMI(Change):
    annual_weight_var: str = VariableValidator(data_type=Decimal, temporal=1)
    height_var: str = VariableValidator(data_type=[Decimal, Integer], temporal=-1)
    annual_bmi_var: str = VariableValidator(data_type=Decimal, temporal=1)

    def __call__(self, composite: Composite):
        h_squared = composite.get_immutable(self.height_var) ** 2
        for period, weight in composite.get_all_observations(self.annual_weight_var):
            bmi = weight / h_squared * 703
            composite.put_observation(self.annual_bmi_var, period, bmi)


@dataclass
class AssignMeanBMI(Change):
    annual_bmi_var: str = VariableValidator(data_type=Decimal, temporal=1)
    mean_bmi_var: str = VariableValidator(data_type=Decimal, temporal=-1)

    def __call__(self, composite: Composite):
        bmis = [bmi for period, bmi in composite.get_all_observations(self.annual_bmi_var)]
        mean_bmi = numpy.average(bmis)
        composite.put_immutable(self.mean_bmi_var, mean_bmi)
