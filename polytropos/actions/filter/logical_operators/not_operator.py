from typing import List

from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema


class Not(LogicalOperator):
    def __init__(self, context: Context, schema: Schema, operands: List[NestableFilter], narrows: bool = True, filters: bool = True):
        assert len(operands) == 1, "Not operator should contain a single child"
        super().__init__(context, schema, operands, narrows, filters)

    def passes_composite(self, composite: Composite) -> bool:
        return not self.operands[0].passes(composite)

    def passes_period(self, composite: Composite, period: str) -> bool:
        return not self.operands[0].passes_period(composite, period)

