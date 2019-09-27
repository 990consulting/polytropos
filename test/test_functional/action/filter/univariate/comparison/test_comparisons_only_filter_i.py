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
        the_filter: Filter = GreaterThan(None, schema, var_id, threshold, narrows=False)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected

    return _do_test

def test_i_text(schema, do_test, composites):
    threshold: str = "c"
    var_id: str = "i_text"
    expected: List[Composite] = [composites[0]]
    do_test(var_id, threshold, expected)

def test_i_integer(schema, do_test, composites):
    threshold: int = 5
    var_id: str = "i_integer"
    expected: List[Composite] = []
    do_test(var_id, threshold, expected)

def test_i_decimal(schema, do_test, composites):
    threshold: float = 20.0
    var_id: str = "i_decimal"
    expected: List[Composite] = []
    do_test(var_id, threshold, expected)

def test_i_currency(schema, do_test, composites):
    threshold: float = 20.0
    var_id: str = "i_currency"
    expected: List[Composite] = []
    do_test(var_id, threshold, expected)

def test_i_date(schema, do_test, composites):
    threshold: str = "2011-01-01"
    var_id: str = "i_date"
    expected: List[Composite] = []
    do_test(var_id, threshold, expected)
