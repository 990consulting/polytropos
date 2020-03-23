from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.ontology.composite import Composite


class Or(LogicalOperator):
    def passes_composite(self, composite: Composite) -> bool:
        for operand in self.operands:
            if operand.passes(composite):
                return True
        return False

    def passes_period(self, composite: Composite, period: str) -> bool:
        for operand in self.operands:
            # We should check operand.passes(composite) to skip not passed composites
            if operand.passes(composite) and operand.passes_period(composite, period):
                return True
        return False
