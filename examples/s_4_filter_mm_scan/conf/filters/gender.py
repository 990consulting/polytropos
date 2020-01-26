from dataclasses import dataclass

from polytropos.actions.filter import Filter
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable.__variable import VariableId


@dataclass
class RetainOnlyFemales(Filter):
    male_flag: VariableId

    def passes(self, composite: Composite) -> bool:
        male: bool = composite.get_immutable(self.male_flag)
        return not male
