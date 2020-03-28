from typing import List

import pytest

from polytropos.actions.filter.logical_operators.not_operator import Not
from polytropos.ontology.composite import Composite
from test.test_functional.action.filter.logical_operator.conftest import check_passes_and_narrow, DummyContainsFilter, create_composite


def test_no_operands(context, schema):
    with pytest.raises(AssertionError):
        Not(context, schema, [], narrows=True, filters=True)


def test_multiple_operands(context, schema):
    with pytest.raises(AssertionError):
        Not(context, schema, [
            DummyContainsFilter(context, schema, True, True, composite_part="1", period_part="p"),
            DummyContainsFilter(context, schema, False, False, composite_part="2", period_part="q"),
        ], narrows=True, filters=True)


@pytest.mark.parametrize("narrows", [True, False])
@pytest.mark.parametrize("filters, narrow_content", [
    (True,
     [
         None,
         {"immutable": "immutable_2", "x": "x_2", "xy": "xy_2"},
     ]),
    (False,
     [
         {"immutable": "immutable_1", "x": "x_1", "y": "y_1"},
         {"immutable": "immutable_2", "x": "x_2", "xy": "xy_2"},
     ]),
])
def test_single_operand(context, schema, narrows, filters, narrow_content):
    operator = Not(context, schema, [
        DummyContainsFilter(context, schema, narrows, filters, composite_part="1", period_part="p"),
    ], narrows=narrows, filters=filters)

    composites: List[Composite] = [
        create_composite(schema, "1", ["p1", "x", "p2", "y", "immutable"]),
        create_composite(schema, "2", ["immutable", "p1", "x", "p2", "xy"])
    ]

    check_passes_and_narrow(composites, narrows, operator, narrow_content)
