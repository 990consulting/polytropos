from dataclasses import dataclass

import numpy

from polytropos.actions.evolve.__change import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId


@dataclass
class AssignAnnualBMI(Change):
    annual_weight_var: VariableId
    height_var: VariableId
    annual_bmi_var: VariableId

    def __call__(self, composite: Composite):
        h_squared = composite.get_immutable(self.height_var) ** 2
        for period, weight in composite.get_all_observations(self.annual_weight_var):
            bmi = weight / h_squared * 703
            composite.put_observation(self.annual_bmi_var, period, bmi)


@dataclass
class AssignMeanBMI(Change):
    annual_bmi_var: VariableId
    mean_bmi_var: VariableId

    def __call__(self, composite: Composite):
        bmis = [bmi for period, bmi in composite.get_all_observations(self.annual_bmi_var)]
        mean_bmi = numpy.average(bmis)
        composite.put_immutable(self.mean_bmi_var, mean_bmi)
