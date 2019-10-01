from typing import Callable, List

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite

from polytropos.actions.filter.univariate.exists import Exists
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def do_test(schema, composites, context) -> Callable:
    def _do_test(var_id: VariableId, expected: List[Composite]):
        the_filter: Filter = Exists(context, schema, var_id, narrows=False)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites))
        assert actual == expected
    return _do_test

@pytest.mark.parametrize("var_id", ["t_Text", "t_Folder", "t_List", "t_KeyedList"])
def test_all(var_id: str, composites, do_test):
    expected = [composites[0]]
    do_test(var_id, expected)
