from abc import ABC
from typing import List, Type, Any, Dict, Union

from polytropos.actions.filter import Filter
from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema


class LogicalOperator(NestableFilter, ABC):
    """Base class for logical filter operators"""

    def __init__(self, context: Context, schema: Schema, operands: List[NestableFilter], narrows: bool = True, filters: bool = True):
        super().__init__(context, schema, narrows, filters)

        assert len(operands) >= 1, "Logical operator should have children"
        for operand in operands:
            assert isinstance(operand, NestableFilter)

        self.operands: List[NestableFilter] = operands

    # noinspection PyMethodOverriding
    @classmethod
    def build_filter(cls, filter_class: Type, context: Context, schema: Schema, filters: bool, narrows: bool, pass_condition: str, operand_specs: List[Union[str, Dict[str, Any]]], **kwargs: Any) -> Filter:  # type: ignore
        operands = []
        for operand_spec in operand_specs:
            assert isinstance(operand_spec, (str, dict))

            if isinstance(operand_spec, str):  # filter name without parameters
                operands.append(cls._build_parameterless_filter(context, schema, operand_spec, filters, narrows, pass_condition))
            else:  # filter name with parameters
                operands.append(cls._build_filter_with_parameters(context, schema, operand_spec, filters, narrows, pass_condition))

        return filter_class(context, schema, operands=operands, narrows=narrows, filters=filters)

    @staticmethod
    def is_logical_operator(class_name: str) -> bool:
        """Checks if a class name is a name of a LogicalOperator descendant.
        NOTE: currently, only direct subclasses are checked."""
        return any(cls.__name__ for cls in LogicalOperator.__subclasses__() if cls.__name__ == class_name)

    @classmethod
    def _build_parameterless_filter(cls, context: Context, schema: Schema, name: str, filters: bool, narrows: bool, pass_condition: str) -> Filter:
        return NestableFilter.build(context, schema, name, filters=filters, narrows=narrows, pass_condition=pass_condition)

    @classmethod
    def _build_filter_with_parameters(cls, context: Context, schema: Schema, operand_spec: Dict[str, Any], filters: bool, narrows: bool, pass_condition: str) -> Filter:
        assert len(operand_spec) == 1
        filter_class_name, filter_spec = operand_spec.popitem()
        if LogicalOperator.is_logical_operator(filter_class_name):
            assert isinstance(filter_spec, list), "LogicalOperator content should be a list"
            return LogicalOperator.build(context, schema, name=filter_class_name, filters=filters, narrows=narrows, pass_condition=pass_condition, operand_specs=filter_spec)

        return NestableFilter.build(context, schema, name=filter_class_name, filters=filters, narrows=narrows, pass_condition=pass_condition, **filter_spec)
