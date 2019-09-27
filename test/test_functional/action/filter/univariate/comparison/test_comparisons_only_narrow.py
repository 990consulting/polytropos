import copy
from collections import Callable
from typing import List

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.comparison import GreaterThan
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def do_test(schema, composites) -> Callable:
    def _do_test(var_id: VariableId, threshold, expected: List[Composite]):
        the_filter: Filter = GreaterThan(None, schema, var_id, threshold, filters=False)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected

    return _do_test

def test_t_text(schema, do_test, composites):
    threshold: str = "c"
    var_id: str = "t_text"
    expected: List[Composite] = [copy.copy(c) for c in composites]
    del expected[0].content["period_2"]
    del expected[0].content["period_3"]
    do_test(var_id, threshold, expected)

def test_t_integer(schema, do_test, composites):
    threshold: int = 5
    var_id: str = "t_integer"
    expected: List[Composite] = [copy.copy(c) for c in composites]
    del expected[0].content["period_2"]
    del expected[0].content["period_3"]
    del expected[1].content["period_1"]
    do_test(var_id, threshold, expected)

def test_t_decimal(schema, do_test, composites):
    threshold: float = 20.0
    var_id: str = "t_decimal"
    expected: List[Composite] = [copy.copy(c) for c in composites]
    for period in expected[0].periods:
        del expected[0].content[period]
    do_test(var_id, threshold, expected)

def test_t_currency(schema, do_test, composites):
    threshold: float = 20.0
    var_id: str = "t_currency"
    expected: List[Composite] = [copy.copy(c) for c in composites]
    del expected[0].content["period_3"]
    del expected[1].content["period_1"]
    do_test(var_id, threshold, expected)

def test_t_date(schema, do_test, composites):
    threshold: str = "2011-01-01"
    var_id: str = "t_date"
    expected: List[Composite] = [copy.copy(c) for c in composites]
    del expected[0].content["period_2"]
    del expected[0].content["period_3"]
    del expected[1].content["period_1"]
    do_test(var_id, threshold, expected)
