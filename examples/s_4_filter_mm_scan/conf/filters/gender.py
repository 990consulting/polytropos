from dataclasses import dataclass

from polytropos.ontology.composite import Composite

from polytropos.actions.filter import Filter
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.variable.__variable import VariableId
from polytropos.ontology.variable import Binary

@dataclass
class RetainOnlyFemales(Filter):
    male_flag: VariableId = VariableValidator(data_type=Binary)

    def passes(self, composite: Composite) -> bool:
        male: bool = composite.get_immutable(self.male_flag)
        return not male
