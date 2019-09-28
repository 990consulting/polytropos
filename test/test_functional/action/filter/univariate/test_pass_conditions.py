from collections import Callable, OrderedDict
from typing import Dict, List, Set
from unittest.mock import MagicMock

import pytest
from polytropos.actions.filter.mem import InMemoryFilterIterator

from polytropos.actions.filter import Filter
from polytropos.actions.filter.univariate.exists import Exists
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture()
def make_track() -> Callable:
    def _make_track(prefix: str) -> Track:
        key: str = "%s_text" % prefix
        spec: Dict = {
            key: {
                "name": key,
                "data_type": "Text",
                "sort_order": 0
            }
        }
        return Track(spec, None, prefix)
    return _make_track

@pytest.fixture()
def schema(make_track) -> Schema:
    immutable: Track = make_track("i")
    temporal: Track = make_track("t")
    return Schema(temporal, immutable)

@pytest.fixture()
def always_composite(schema) -> Composite:
    content: Dict = {
        "period_1": {
            "t_text": "A"
        },
        "period_2": {
            "t_text": "B"
        },
        "period_3": {
            "t_text": "C"
        }
    }
    return Composite(schema, content, composite_id="always")

@pytest.fixture()
def immutable_only_composite(schema) -> Composite:
    content: Dict = {
        "immutable": {
            "i_text": "D"
        }
    }
    return Composite(schema, content, composite_id="immutable_only")

@pytest.fixture()
def never_composite(schema) -> Composite:
    content: Dict = {
        "period_1": {},
        "period_2": {},
        "period_3": {},
        "immutable": {
            "i_text": "D"
        }
    }
    return Composite(schema, content, composite_id="never")

@pytest.fixture()
def middle_composite(schema) -> Composite:
    content: Dict = {
        "period_1": {},
        "period_2": {
            "t_text": "B"
        },
        "period_3": {}
    }
    return Composite(schema, content, composite_id="middle")

@pytest.fixture()
def earliest_composite(schema) -> Composite:
    content: Dict = {
        "period_1": {
            "t_text": "A"
        },
        "period_2": {},
        "period_3": {}
    }
    return Composite(schema, content, composite_id="earliest")

@pytest.fixture()
def latest_composite(schema) -> Composite:
    content: Dict = {
        "period_1": {},
        "period_2": {},
        "period_3": {
            "t_text": "C"
        }
    }
    return Composite(schema, content, composite_id="latest")

@pytest.fixture()
def composites(always_composite, immutable_only_composite, never_composite, middle_composite, earliest_composite,
               latest_composite) -> Dict[str, Composite]:

    return OrderedDict([
        ("always", always_composite),
        ("immutable_only", immutable_only_composite),
        ("never", never_composite),
        ("middle", middle_composite),
        ("earliest", earliest_composite),
        ("latest", latest_composite)
    ])

@pytest.fixture()
def do_test(schema: Schema, composites: Dict) -> Callable:
    def _do_test(var_id: str, pass_condition: str, expected_keys: List[str]) -> None:
        context: Context = MagicMock(spec=Context)
        the_filter: Filter = Exists(context, schema, var_id, narrows=False, pass_condition=pass_condition)
        f_iter: Callable = InMemoryFilterIterator([the_filter])
        actual: List[Composite] = list(f_iter(composites.values()))
        expected: List[Composite] = []
        for key in expected_keys:
            expected.append(composites[key])
        assert actual == expected
    return _do_test

@pytest.mark.parametrize("pass_condition, expected_keys", [
    ("all", ["always"]),
    ("any", ["always", "middle", "earliest", "latest"]),
    ("earliest", ["always", "earliest"]),
    ("latest", ["always", "latest"]),
    ("never", ["immutable_only", "never"])
])
def test_temporal_cases(pass_condition: str, expected_keys: List[str], do_test: Callable) -> None:
    do_test("t_text", pass_condition, expected_keys)

@pytest.mark.parametrize("pass_condition", ["all", "any", "earliest", "latest", "never"])
def test_immutable_cases(pass_condition: str, do_test: Callable) -> None:
    expected_keys: List[str] = ["immutable_only", "never"]
    do_test("i_text", pass_condition, expected_keys)

@pytest.mark.parametrize("pass_condition", ["ALL", "All"])
def test_case_ignored(pass_condition: str, do_test: Callable) -> None:
    do_test("t_text", pass_condition, ["always"])
