import logging
from abc import ABC
from typing import List, Any, Type

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.__univariate import BaseUnivariateFilter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema
from polytropos.util.loader import load


class LogicalOperator(BaseUnivariateFilter, ABC):
    def __init__(self, context: Context, schema: Schema, operands: List[BaseUnivariateFilter],
                 narrows: bool = True, filters: bool = True):
        super().__init__(context, schema, narrows, filters)

        assert len(operands) >= 1, "Logical operator should have children"
        for operand in operands:
            assert isinstance(operand, BaseUnivariateFilter)

        self.operands: List[BaseUnivariateFilter] = operands

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
