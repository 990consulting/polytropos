from dataclasses import dataclass
from typing import Dict
import numpy

from polytropos.actions.evolve.__change import Change
from polytropos.actions.evolve.__subject import SubjectValidator
from polytropos.ontology.variable import Decimal, Integer, Primitive
from polytropos.util import composites


@dataclass
class AssignAnnualBMI(Change):
    annual_weight_var: Decimal = SubjectValidator(data_type=Decimal, temporal=1)
    height_var: Primitive = SubjectValidator(data_type=[Decimal, Integer], temporal=-1)
    annual_bmi_var: Decimal = SubjectValidator(data_type=Decimal, temporal=1)

    def __call__(self, composite: Dict):
        h_squared = composites.get_property(composite, self.height_var) ** 2
        for period, weight in composites.get_all_observations(composite, self.annual_weight_var):
            bmi = weight / h_squared * 703
            composites.put_observation(composite, period, self.annual_bmi_var, bmi)


@dataclass
class AssignMeanBMI(Change):
    annual_bmi_var: Decimal = SubjectValidator(data_type=Decimal, temporal=1)
    mean_bmi_var: Decimal = SubjectValidator(data_type=Decimal, temporal=-1)

    def __call__(self, composite: Dict):
        bmis = [bmi for period, bmi in composites.get_all_observations(composite, self.annual_bmi_var)]
        mean_bmi = numpy.average(bmis)
        composites.put_property(composite, self.mean_bmi_var, mean_bmi)
