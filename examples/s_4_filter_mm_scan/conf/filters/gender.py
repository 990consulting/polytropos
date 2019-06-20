from dataclasses import dataclass
from typing import Dict

from polytropos.ontology.composite import Composite

from polytropos.actions.filter import Filter
from polytropos.actions.validator import VariableValidator
from polytropos.ontology.variable.__variable import Binary

@dataclass
class RetainOnlyFemales(Filter):
    male_flag: str = VariableValidator(data_type=Binary)

    def passes(self, composite: Composite) -> bool:
        male: bool = composite.get_immutable(self.male_flag)
        return not male
