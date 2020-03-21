from abc import ABC
from typing import List, Type

from polytropos.actions.filter import Filter
from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema


class LogicalOperator(NestableFilter, ABC):
    def __init__(self, context: Context, schema: Schema, operands: List[NestableFilter], narrows: bool = True, filters: bool = True):
        super().__init__(context, schema, narrows, filters)

        assert len(operands) >= 1, "Logical operator should have children"
        for operand in operands:
            assert isinstance(operand, NestableFilter)

        self.operands: List[NestableFilter] = operands

    # noinspection PyMethodOverriding
    @classmethod
    def build_filter(cls, filter: Type, context: Context, schema: Schema, operands: List[str], **kwargs):  # type: ignore
        operator_operands = []
        for operand_spec in operands:
            if isinstance(operand_spec, str):
                operator_operands.append(Filter.build(context, schema, name=operand_spec))
            elif isinstance(operand_spec, dict):
                for name, spec in operand_spec.items():
                    operator_operands.append(Filter.build(context, schema, name=name, **spec))
        return filter(context, schema, operator_operands)
