from unittest.mock import MagicMock

import pytest
import yaml

from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.actions.filter.logical_operators.or_operator import Or
from polytropos.actions.filter.logical_operators.and_operator import And
from polytropos.actions.filter.logical_operators.not_operator import Not
from polytropos.actions.filter.nested_filter import NestedFilter
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

class DummyFilter(NestableFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, pass_condition: str):
        super().__init__(context, schema, narrows, filters)
        self.pass_condition = pass_condition

    def passes_composite(self, composite: Composite) -> bool:
        pass

    def passes_period(self, composite: Composite, period: str) -> bool:
        pass


class Filter1(DummyFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, pass_condition: str, param11: str, param12: str):
        super().__init__(context, schema, narrows, filters, pass_condition)
        self.param11 = param11
        self.param12 = param12


class Filter2(DummyFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, pass_condition: str, param21: str = "default21"):
        super().__init__(context, schema, narrows, filters, pass_condition)
        self.param21 = param21


class Filter3(DummyFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, pass_condition: str, param31: str = "default31", param32: int = 32):
        super().__init__(context, schema, narrows, filters, pass_condition)
        self.param31 = param31
        self.param32 = param32


class Filter4(DummyFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, pass_condition: str, param41: str = "default41"):
        super().__init__(context, schema, narrows, filters, pass_condition)
        self.param41 = param41


class Filter5(DummyFilter):
    def __init__(self, context: Context, schema: Schema, narrows: bool, filters: bool, pass_condition: str, param51: str):
        super().__init__(context, schema, narrows, filters, pass_condition)
        self.param51 = param51


@pytest.fixture()
def context() -> Context:
    return MagicMock()


@pytest.fixture()
def schema() -> Schema:
    return MagicMock()


def test_empty_content(context, schema):
    with pytest.raises(AssertionError, match="NestedFilter content should contain the only direct child"):
        NestedFilter(context, schema, {}, True, False, "any")


def test_array_content(context, schema):
    content = yaml.load("""
    - Or
    """, yaml.Loader)
    with pytest.raises(AssertionError, match="NestedFilter content should be a dictionary"):
        NestedFilter(context, schema, content, True, False, "any")


def test_multiple_content(context, schema):
    content = yaml.load("""
    Or:
    And:
    """, yaml.Loader)
    with pytest.raises(AssertionError, match="NestedFilter content should contain the only direct child"):
        NestedFilter(context, schema, content, True, False, "any")


@pytest.mark.parametrize("parameter", ["filters", "narrows", "pass_condition"])
def test_nested_parameter(context, schema, parameter):
    content = yaml.load(f"""
    Or:
      - And:
        - Filter1:
            {parameter}: true
        - Filter2
    """, yaml.Loader)
    with pytest.raises(TypeError, match=f"got multiple values for keyword argument '{parameter}'"):
        NestedFilter(context, schema, content, True, True, "any")


@pytest.mark.parametrize("narrows", [True, False])
@pytest.mark.parametrize("filters", [True, False])
@pytest.mark.parametrize("pass_condition", ["any", "all", "never"])
def test_nested_logical_operators(context, schema, narrows, filters, pass_condition):
    content = yaml.load("""
    Or:
      - And:
        - Filter1:
            param11: value11
            param12: value12
        - Filter2
      - Filter3
      - Filter4:
          param41: value41
      - Not:
        - Filter5:
            param51: value51  
    """, yaml.Loader)
    nested_filter = NestedFilter(context, schema, content, filters, narrows, pass_condition)

    root_node: Or = nested_filter.child
    assert isinstance(root_node, Or)
    assert root_node.filters == filters
    assert root_node.narrows == narrows
    assert len(root_node.operands) == 4

    child0: And = root_node.operands[0]
    assert isinstance(child0, And)
    assert child0.filters == filters
    assert child0.narrows == narrows
    assert len(child0.operands) == 2

    child1: Filter3 = root_node.operands[1]
    assert isinstance(child1, Filter3)
    assert child1.filters == filters
    assert child1.narrows == narrows
    assert child1.pass_condition == pass_condition
    assert child1.param31 == "default31"
    assert child1.param32 == 32

    child2: Filter4 = root_node.operands[2]
    assert isinstance(child2, Filter4)
    assert child2.filters == filters
    assert child2.narrows == narrows
    assert child2.pass_condition == pass_condition
    assert child2.param41 == "value41"

    child3: Not = root_node.operands[3]
    assert isinstance(child3, Not)
    assert child3.filters == filters
    assert child3.narrows == narrows
    assert len(child3.operands) == 1

    child0_0: Filter1 = child0.operands[0]
    assert isinstance(child0_0, Filter1)
    assert child0_0.filters == filters
    assert child0_0.narrows == narrows
    assert child0_0.pass_condition == pass_condition
    assert child0_0.param11 == "value11"
    assert child0_0.param12 == "value12"

    child0_1: Filter2 = child0.operands[1]
    assert isinstance(child0_1, Filter2)
    assert child0_1.filters == filters
    assert child0_1.narrows == narrows
    assert child0_1.pass_condition == pass_condition
    assert child0_1.param21 == "default21"

    child3_0: Filter5 = child3.operands[0]
    assert isinstance(child3_0, Filter5)
    assert child3_0.filters == filters
    assert child3_0.narrows == narrows
    assert child3_0.pass_condition == pass_condition
    assert child3_0.param51 == "value51"


@pytest.mark.parametrize("narrows", [True, False])
@pytest.mark.parametrize("filters", [True, False])
@pytest.mark.parametrize("pass_condition", ["any", "all", "never"])
def test_nested_filter(context, schema, narrows, filters, pass_condition):
    content = yaml.load("""
    
    Filter3:
      param32: 132
    """, yaml.Loader)
    nested_filter = NestedFilter(context, schema, content, filters, narrows, pass_condition)

    child0: Filter3 = nested_filter.child
    assert isinstance(child0, Filter3)
    assert child0.filters == filters
    assert child0.narrows == narrows
    assert child0.pass_condition == pass_condition
    assert child0.param31 == "default31"
    assert child0.param32 == 132
