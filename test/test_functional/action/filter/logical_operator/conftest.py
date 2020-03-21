import copy
from typing import List, Any
from unittest.mock import MagicMock

import pytest

from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.actions.filter.logical_operators._logical_operator import LogicalOperator
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema


@pytest.fixture()
def context() -> Context:
    return MagicMock()


@pytest.fixture()
def schema() -> Schema:
    return MagicMock()


class DummyContainsFilter(NestableFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, composite_part: str, period_part: str):
        super().__init__(context, schema, narrows, filters)
        self.composite_part = composite_part
        self.period_part = period_part

    def passes_composite(self, composite: Composite) -> bool:
        return self.composite_part in composite.composite_id

    def passes_period(self, composite: Composite, period: str) -> bool:
        return self.period_part in period


def create_composite(schema: Schema, composite_id: str, periods: List[str]) -> Composite:
    return Composite(schema, {period: f"{period}_{composite_id}" for period in periods}, composite_id)


def check_passes_and_narrow(composites: List[Composite], narrows: bool, operator: LogicalOperator, narrow_content: List[Any]):
    for i, composite in enumerate(composites):
        assert operator.passes(composite) == (narrow_content[i] is not None)
        if narrow_content[i] is not None:
            expected_content = narrow_content[i] if narrows else copy.copy(composite.content)
            operator.narrow(composite)
            assert composite.content == expected_content
