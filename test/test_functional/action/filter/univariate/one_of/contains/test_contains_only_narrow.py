import copy
from collections import Callable
from typing import List, Set, Dict

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.one_of import ContainsOneOf
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite

@pytest.fixture()
def do_test(schema, composites) -> Callable:
    def _do_test(values: List[str], keys: List[Set[str]]):
        expected: List[Composite] = []
        for i, i_keys in enumerate(keys):
            content: Dict = {}
            for key in i_keys:
                content[key] = composites[i].content[key]
            composite: Composite = Composite(schema, content, composite_id=composites[i].composite_id)
            expected.append(composite)
            
        the_filter: Filter = ContainsOneOf(None, schema, "t_text", values=values, filters=False)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected
        
    return _do_test

def test_abc(do_test):
    values: List[str] = ["abc"]
    keys: List[Set[str]] = [
        {"period_1", "immutable"},
        {"immutable"}
    ]
    do_test(values, keys)

def test_abc_def(do_test):
    values: List[str] = ["abc", "def"]
    keys: List[Set[str]] = [
        {"period_1", "period_2", "immutable"},
        {"immutable"}
    ]
    do_test(values, keys)

def test_abc_012(do_test):
    values: List[str] = ["abc", "012"]
    keys: List[Set[str]] = [
        {"period_1", "immutable"},
        {"period_1", "immutable"}
    ]
    do_test(values, keys)

def test_ghi(do_test):
    values: List[str] = ["ghi"]
    keys: List[Set[str]] = [
        {"immutable"},
        {"immutable"}
    ]
    do_test(values, keys)

def test_a(do_test):
    values: List[str] = ["a"]
    keys: List[Set[str]] = [
        {"period_1", "immutable"},
        {"immutable"}
    ]
    do_test(values, keys)

def test_a_1(do_test):
    values: List[str] = ["a", "1"]
    keys: List[Set[str]] = [
        {"period_1", "immutable"},
        {"period_1", "immutable"}
    ]
    do_test(values, keys)

def test_g(do_test):
    values: List[str] = ["g"]
    keys: List[Set[str]] = [
        {"immutable"},
        {"immutable"}
    ]
    do_test(values, keys)

def test_g_6(do_test):  # I built this whole test suite around this pun
    values: List[str] = ["g", "6"]
    keys: List[Set[str]] = [
        {"immutable"},
        {"immutable"}
    ]
    do_test(values, keys)

# noinspection PyPep8Naming
def test_ABC(do_test):
    values: List[str] = ["ABC"]
    keys: List[Set[str]] = [
        {"period_1", "immutable"},
        {"immutable"}
    ]
    do_test(values, keys)
