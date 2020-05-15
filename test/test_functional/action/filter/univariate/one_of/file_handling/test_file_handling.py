"""Test that OneOfFilters can handle match options specified in a file, with one match option specified on each line."""

import copy
import os
from collections import Callable
from typing import List, Set, Dict

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.one_of import ContainsOneOf
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite

@pytest.fixture()
def get_file_name(basepath) -> Callable:
    def _get_file_name(case_name) -> str:
        rel_path: str = "test_functional/action/filter/univariate/one_of/file_handling"
        file_name: str = "{}/{}/{}.txt".format(basepath, rel_path, case_name)
        return file_name
    return _get_file_name

@pytest.mark.parametrize("case_name", ["nominal", "extra_whitespace"])
def test_values_from_file(schema, composites, get_file_name, case_name) -> None:
    file_name: str = get_file_name(case_name)
    keys: List[Set[str]] = [
        {"period_1", "period_2", "immutable"},
        {"immutable"}
    ]

    expected: List[Composite] = []
    for i, i_keys in enumerate(keys):
        content: Dict = {}
        for key in i_keys:
            content[key] = composites[i].content[key]
        composite: Composite = Composite(schema, content, composite_id=composites[i].composite_id)
        expected.append(composite)

    the_filter: Filter = ContainsOneOf(None, schema, "t_text", file_name=file_name, filters=False)
    f_iter: Callable = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composites))
    assert actual == expected

@pytest.mark.parametrize("case_name", ["empty", "empty_line"])
def test_corrupt_file_raises(schema, get_file_name, case_name) -> None:
    file_name: str = get_file_name(case_name)
    with pytest.raises(ValueError):
        ContainsOneOf(None, schema, "t_text", file_name=file_name, filters=False)

def test_non_existent_file_raises(schema, basepath) -> None:
    file_name: str = "/path/to/file/that/does/not/exist"
    if os.path.exists(file_name):
        pytest.fail("{} actually exists. Can't run test.".format(file_name))
    with pytest.raises(FileNotFoundError):
        ContainsOneOf(None, schema, "t_text", file_name=file_name, filters=False)
