from typing import Dict, cast, Callable

import pytest
from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable, VariableId

@pytest.fixture()
def temporal_track() -> Track:
    spec: Dict = {
        "the_temporal_var": {
            "name": "temporal variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    return Track.build(spec, None, "temporal")

@pytest.fixture()
def immutable_track() -> Track:
    spec: Dict = {
        "the_immutable_var": {
            "name": "immutable variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    return Track.build(spec, None, "immutable")

@pytest.fixture()
def schema(temporal_track, immutable_track) -> Schema:
    return Schema(temporal_track, immutable_track)

def test_temporal_yes(schema):
    var: Variable = schema.get(cast(VariableId, "the_temporal_var"))
    assert var.temporal

def test_temporal_no(schema):
    var: Variable = schema.get(cast(VariableId, "the_immutable_var"))
    assert not var.temporal

@pytest.fixture()
def do_nearest_list_test() -> Callable:
    def _do_nearest_list_test(innermost: str, middle: str, outermost: str, expected: str) -> None:
        spec: Dict = {
            "innermost": {
                "data_type": innermost,
                "name": "innermost",
                "sort_order": 0,
                "parent": "middle"
            },
            "middle": {
                "data_type": middle,
                "name": "middle",
                "sort_order": 0,
                "parent": "outermost"
            },
            "outermost": {
                "data_type": outermost,
                "name": "outermost",
                "sort_order": 0
            }
        }
        immutable: Track = Track.build(spec, None, "i")
        temporal: Track = Track.build({}, None, "t")
        schema: Schema = Schema(temporal, immutable)
        innermost: Variable = schema.get(cast(VariableId, "innermost"))
        assert innermost.nearest_list == expected
    return _do_nearest_list_test

def test_nearest_list_parent(do_nearest_list_test):
    do_nearest_list_test("Text", "List", "Folder", "middle")

def test_nearest_list_grandparent(do_nearest_list_test):
    do_nearest_list_test("Text", "Folder", "List", "outermost")

def test_nearest_list_not_self(do_nearest_list_test):
    do_nearest_list_test("List", "Folder", "List", "outermost")

def test_nearest_list_not_from_list_raises(do_nearest_list_test):
    with pytest.raises(AttributeError):
        do_nearest_list_test("Text", "Folder", "Folder", "SHOULD NOT BE CHECKED")
