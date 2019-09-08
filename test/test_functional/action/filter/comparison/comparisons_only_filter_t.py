import copy
from collections import Callable
from typing import List

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.comparison import GreaterThan
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def do_test(schema, composites) -> Callable:
    def _do_test(var_id: VariableId, threshold, expected: List[Composite]):
        the_filter: Filter = GreaterThan(schema, var_id, threshold, narrows=False)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected
    return _do_test

def test_t_text(schema, do_test, composites):
    threshold: str = "c"
    var_id: str = "t_text"
    expected: List[Composite] = [copy.copy(c) for c in composites]
    do_test(var_id, threshold, expected)

def test_t_integer(schema, do_test, composites):
    threshold: int = 5
    var_id: str = "t_integer"
    expected: List[Composite] = [composites[0]]
    do_test(var_id, threshold, expected)

def test_t_decimal(schema, do_test, composites):
    threshold: float = 20.0
    var_id: str = "t_decimal"
    expected: List[Composite] = [composites[1]]
    do_test(var_id, threshold, expected)

def test_t_currency(schema, do_test, composites):
    threshold: float = 20.0
    var_id: str = "t_currency"
    expected: List[Composite] = [composites[0]]
    do_test(var_id, threshold, expected)

def test_t_date(schema, do_test, composites):
    threshold: str = "2011-01-01"
    var_id: str = "t_date"
    expected: List[Composite] = [composites[0]]
    do_test(var_id, threshold, expected)
