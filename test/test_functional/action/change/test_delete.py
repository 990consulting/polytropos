import copy
from collections import Callable
from typing import Dict, List, cast

import pytest

from polytropos.actions.changes.delete import Delete
from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def make_track() -> Callable:
    def _make_track(name: str) -> Track:
        spec: Dict = {
            "%s_text_in_root" % name: {
                "name": "%s_text_in_root" % name,
                "data_type": "Text",
                "sort_order": 0
            },
            "%s_list_in_root" % name: {
                "name": "%s_list_in_root" % name,
                "data_type": "List",
                "sort_order": 1
            },
            "%s_text_in_list" % name: {
                "name": "some_text",
                "data_type": "Text",
                "parent": "%s_list_in_root" % name,
                "sort_order": 0
            },
            "%s_keyed_list_in_root" % name: {
                "name": "%s_keyed_list_in_root" % name,
                "data_type": "List",
                "sort_order": 2
            },
            "%s_text_in_keyed_list" % name: {
                "name": "some_text",
                "data_type": "Text",
                "parent": "%s_keyed_list_in_root" % name,
                "sort_order": 0
            }
        }
        return Track.build(spec, None, name)
    return _make_track

@pytest.fixture()
def schema(make_track) -> Schema:
    temporal: Track = make_track("temporal")
    immutable: Track = make_track("immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def content() -> Dict:
    return {
        "201112": {
            "temporal_text_in_root": "abc",
            "temporal_list_in_root": [
                {"some_text": "AAA"},
                {"some_text": "BBB"},
            ],
            "temporal_keyed_list_in_root": {
                "x": {"some_text": "AAA"},
                "y": {"some_text": "BBB"}
            }
        },
        "201212": {
            "temporal_text_in_root": "abc",
            "temporal_list_in_root": [
                {"some_text": "AAA"},
                {"some_text": "BBB"},
            ],
            "temporal_keyed_list_in_root": {
                "x": {"some_text": "AAA"},
                "y": {"some_text": "BBB"}
            }
        },
        "immutable": {
            "immutable_text_in_root": "abc",
            "immutable_list_in_root": [
                {"some_text": "AAA"},
                {"some_text": "BBB"},
            ],
            "immutable_keyed_list_in_root": {
                "x": {"some_text": "AAA"},
                "y": {"some_text": "BBB"}
            }
        }
    }

@pytest.fixture()
def do_test(schema, content) -> Callable:
    def _do_test(targets: List[str], expected: Dict) -> None:
        composite: Composite = Composite(schema, content)
        target_ids: List[VariableId] = [cast(VariableId, x) for x in targets]
        change: Change = Delete(schema, {}, target_ids)
        change(composite)
        assert composite.content == expected
    return _do_test

def test_delete_immutable_singleton(do_test, content):
    targets: List[str] = ["temporal_text_in_root"]
    expected: Dict = copy.deepcopy(content)
    del expected["201112"]["temporal_text_in_root"]
    del expected["201212"]["temporal_text_in_root"]
    do_test(targets, expected)

def test_delete_temporal_singleton(content, do_test):
    targets: List[str] = ["immutable_text_in_root"]
    expected: Dict = copy.deepcopy(content)
    del expected["immutable"]["immutable_text_in_root"]
    do_test(targets, expected)

def test_both_singletons(content, do_test):
    targets: List[str] = ["temporal_text_in_root", "immutable_text_in_root"]
    expected: Dict = copy.deepcopy(content)
    del expected["201112"]["temporal_text_in_root"]
    del expected["201212"]["temporal_text_in_root"]
    del expected["immutable"]["immutable_text_in_root"]
    do_test(targets, expected)

def test_delete_item_from_immutable_list(content, do_test):
    targets: List[str] = ["immutable_text_in_list"]
    expected: Dict = copy.deepcopy(content)
    for element in expected["immutable"]["immutable_list_in_root"]:
        del element["some_text"]
    do_test(targets, expected)

def test_delete_item_from_both_lists(content, do_test):
    targets: List[str] = ["immutable_text_in_list", "temporal_text_in_list"]
    expected: Dict = copy.deepcopy(content)
    for element in expected["immutable"]["immutable_list_in_root"]:
        del element["some_text"]
    for period in ["201112", "201212"]:
        for element in expected[period]["temporal_list_in_root"]:
            del element["some_text"]
    do_test(targets, expected)

def test_delete_item_from_immutable_keyed_list(content, do_test):
    targets: List[str] = ["immutable_text_in_keyed_list"]
    expected: Dict = copy.deepcopy(content)
    for element in expected["immutable"]["immutable_keyed_list_in_root"].values():
        del element["some_text"]
    do_test(targets, expected)

def test_delete_item_from_both_keyed_lists(content, do_test):
    targets: List[str] = ["immutable_text_in_keyed_list", "temporal_text_in_keyed_list"]
    expected: Dict = copy.deepcopy(content)
    for element in expected["immutable"]["immutable_keyed_list_in_root"].values():
        del element["some_text"]
    for period in ["201112", "201212"]:
        for element in expected[period]["temporal_keyed_list_in_root"].values():
            del element["some_text"]
    do_test(targets, expected)

def test_delete_list_itself(content, do_test):
    targets: List[str] = ["immutable_text_in_root", "temporal_list_in_root"]
    expected: Dict = copy.deepcopy(content)
    del expected["immutable"]["immutable_text_in_root"]
    del expected["201112"]["temporal_list_in_root"]
    del expected["201212"]["temporal_list_in_root"]
    do_test(targets, expected)
