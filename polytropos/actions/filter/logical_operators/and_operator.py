from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.ontology.composite import Composite


class And(LogicalOperator):
    def passes_composite(self, composite: Composite) -> bool:
        for operand in self.operands:
            if not operand.passes(composite):
                return False
        return True

    def passes_period(self, composite: Composite, period: str) -> bool:
        for operand in self.operands:
            # operand.passes(composite) is always True and so it is removed from condition below
            if not operand.passes_period(composite, period):
                return False
        return True
