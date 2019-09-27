from typing import Callable, List

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite

from polytropos.actions.filter.exists import Exists
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def do_test(schema, composites, context) -> Callable:
    def _do_test(var_id: VariableId, expected: List[Composite]):
        the_filter: Filter = Exists(context, schema, var_id, narrows=False)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected
    return _do_test

def test_primitive(composites, do_test):
    var_id: str = "i_Text"
    expected = [composites[1], composites[2]]  # Empty string is considered to "exist"
    do_test(var_id, expected)

def test_folder(composites, do_test):
    var_id: str = "i_Folder"
    expected = [composites[2]]
    do_test(var_id, expected)

def test_list(composites, do_test):
    var_id: str = "i_List"
    expected = [composites[2]]
    do_test(var_id, expected)

def test_keyed_list(composites, do_test):
    var_id: str = "i_KeyedList"
    expected = [composites[2]]
    do_test(var_id, expected)
