from abc import ABC
from typing import List, Type, Any, Dict, Union

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
    def build_filter(cls, filter_class: Type, context: Context, schema: Schema, filters: bool, narrows: bool, pass_condition: str, operand_specs: List[Union[str, Dict[str, Any]]], **kwargs):  # type: ignore
        operands = []
        for operand_spec in operand_specs:
            if isinstance(operand_spec, str):
                operands.append(NestableFilter.build(context, schema, name=operand_spec, filters=filters, narrows=narrows, pass_condition=pass_condition))
            elif isinstance(operand_spec, dict):
                for name, spec in operand_spec.items():
                    if isinstance(spec, list):
                        operands.append(LogicalOperator.build(context, schema, name=name, filters=filters, narrows=narrows, pass_condition=pass_condition, operand_specs=spec))
                    else:
                        operands.append(NestableFilter.build(context, schema, name=name, filters=filters, narrows=narrows, pass_condition=pass_condition, **spec))
        return filter_class(context, schema, operands=operands, narrows=narrows, filters=filters)
