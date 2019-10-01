from collections import Callable
from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from polytropos.actions.filter.mem import InMemoryFilterIterator

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.exists import DoesNotExist
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema

@pytest.fixture()
def do_test(schema: Schema, composites: Dict) -> Callable:
    def _do_test(var_id: str, pass_condition: str, expected_keys: List[str]) -> None:
        context: Context = MagicMock(spec=Context)
        the_filter: Filter = DoesNotExist(context, schema, var_id, narrows=False, pass_condition=pass_condition)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites.values()))
        expected: List[Composite] = []
        for key in expected_keys:
            expected.append(composites[key])
        assert actual == expected
    return _do_test

@pytest.mark.parametrize("pass_condition, expected_keys", [
    ("all", ["immutable_only", "never"]),
    ("any", ["immutable_only", "never", "middle", "earliest", "latest"]),
    ("earliest", ["immutable_only", "never", "middle", "latest"]),
    ("latest", ["immutable_only", "never", "middle", "earliest"]),
    ("never", ["always", "immutable_only"])
])
def test_temporal_cases(pass_condition: str, expected_keys: List[str], do_test: Callable) -> None:
    do_test("t_text", pass_condition, expected_keys)

@pytest.mark.parametrize("pass_condition", ["all", "any", "earliest", "latest", "never"])
def test_immutable_cases(pass_condition: str, do_test: Callable) -> None:
    expected_keys: List[str] = ["always", "middle", "earliest", "latest"]  # None of these have immutable periods
    do_test("i_text", pass_condition, expected_keys)
