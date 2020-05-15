from collections import Callable
from typing import List

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.one_of import MatchesOneOf
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite

@pytest.fixture()
def do_test(schema, composites) -> Callable:
    def _do_test(values: List[str], expected: List[Composite]):
        the_filter: Filter = MatchesOneOf(None, schema, "t_text", values=values)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected
    return _do_test

def test_abc(do_test, composites):
    values: List[str] = ["abc"]
    expected: List[Composite] = [composites[0]]
    del expected[0].content["period_2"]
    do_test(values, expected)

def test_abc_def(do_test, composites):
    values: List[str] = ["abc", "def"]
    expected: List[Composite] = [composites[0]]
    do_test(values, expected)

def test_abc_012(do_test, composites):
    values: List[str] = ["abc", "012"]
    expected: List[Composite] = list(composites)
    del expected[0].content["period_2"]
    del expected[1].content["period_2"]
    do_test(values, expected)

def test_ghi(do_test):
    values: List[str] = ["ghi"]
    expected: List[Composite] = []
    do_test(values, expected)

def test_a(do_test, composites):
    values: List[str] = ["a"]
    expected: List[Composite] = []
    do_test(values, expected)

def test_a_1(do_test, composites):
    values: List[str] = ["a", "1"]
    expected: List[Composite] = []
    do_test(values, expected)

def test_g(do_test, composites):
    values: List[str] = ["g"]
    expected: List[Composite] = []
    do_test(values, expected)

def test_g_6(do_test, composites):  # I built this whole test suite around this pun
    values: List[str] = ["g", "6"]
    expected: List[Composite] = []
    do_test(values, expected)

# noinspection PyPep8Naming
def test_ABC(do_test, composites):
    values: List[str] = ["ABC"]
    expected: List[Composite] = [composites[0]]
    del expected[0].content["period_2"]
    do_test(values, expected)
