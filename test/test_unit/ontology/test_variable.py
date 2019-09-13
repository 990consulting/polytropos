from typing import Dict

import pytest
from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

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
    var: Variable = schema.get("the_temporal_var")
    assert var.temporal

def test_temporal_no(schema):
    var: Variable = schema.get("the_immutable_var")
    assert not var.temporal

def test_nearest_list_parent():
    pytest.fail()

def test_nearest_list_grandparent():
    pytest.fail()