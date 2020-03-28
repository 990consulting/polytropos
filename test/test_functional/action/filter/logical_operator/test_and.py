from typing import List

import pytest

from polytropos.actions.filter.logical_operators.and_operator import And
from polytropos.ontology.composite import Composite
from test.test_functional.action.filter.logical_operator.conftest import check_passes_and_narrow, DummyContainsFilter, create_composite


def test_no_operands(context, schema):
    with pytest.raises(AssertionError):
        And(context, schema, [], narrows=True, filters=True)


@pytest.mark.parametrize("narrows", [True, False])
@pytest.mark.parametrize("filters, narrow_content", [
    (True,
     [
         {"immutable": "immutable_1", "p1": "p1_1", "p2": "p2_1"},
         None,
     ]),
    (False,
     [
         {"immutable": "immutable_1", "p1": "p1_1", "p2": "p2_1"},
         {"immutable": "immutable_2", "p1": "p1_2", "p2": "p2_2"},
     ]),
])
def test_single_operand(context, schema, narrows, filters, narrow_content):
    operator = And(context, schema, [
        DummyContainsFilter(context, schema, narrows, filters, composite_part="1", period_part="p"),
    ], narrows=narrows, filters=filters)

    composites: List[Composite] = [
        create_composite(schema, "1", ["p1", "x", "p2", "immutable"]),
        create_composite(schema, "2", ["immutable", "p1", "x", "p2"])
    ]

    check_passes_and_narrow(composites, narrows, operator, narrow_content)


@pytest.mark.parametrize("narrows", [True, False])
@pytest.mark.parametrize("filters, narrow_content", [
    (True,
     [
         {"immutable": "immutable_12", "pq": "pq_12"},
         {"immutable": "immutable_21", "pq": "pq_21", "qp": "qp_21"},
         None,
         None,
     ]),
    (False,
     [
         {"immutable": "immutable_12", "pq": "pq_12"},
         {"immutable": "immutable_21", "pq": "pq_21", "qp": "qp_21"},
         {"immutable": "immutable_11", "pq": "pq_11"},
         {"immutable": "immutable_22", "qp": "qp_22"},
     ]),
])
def test_two_operands(context, schema, narrows, filters, narrow_content):
    operator = And(context, schema, [
        DummyContainsFilter(context, schema, narrows, filters, composite_part="1", period_part="p"),
        DummyContainsFilter(context, schema, narrows, filters, composite_part="2", period_part="q"),
    ], narrows=narrows, filters=filters)

    composites: List[Composite] = [
        create_composite(schema, "12", ["p", "q", "pq", "py", "immutable"]),
        create_composite(schema, "21", ["qp", "pq", "p", "qx", "immutable"]),
        create_composite(schema, "11", ["immutable", "pq", "x", "p"]),
        create_composite(schema, "22", ["immutable", "qp", "y", "q"]),
    ]

    check_passes_and_narrow(composites, narrows, operator, narrow_content)
