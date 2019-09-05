from dataclasses import dataclass

from polytropos.util.nesteddicts import MissingDataError

from polytropos.ontology.composite import Composite

from polytropos.actions.filter import Filter
from polytropos.ontology.variable import VariableId

@dataclass
class ImmutableValueThreshold(Filter):
    threshold_var: VariableId
    threshold: int

    def passes(self, composite: Composite) -> bool:
        try:
            value: int = composite.get_immutable(self.threshold_var)
        except MissingDataError:
            return False

        return value >= self.threshold