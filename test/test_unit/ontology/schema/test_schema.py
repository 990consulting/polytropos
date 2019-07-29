import copy
from typing import Dict

import pytest

from polytropos.ontology.schema import Schema, TrackType, DuplicatePathError
from polytropos.ontology.track import Track

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

def test_get_immutable(immutable_track, schema):
    expected = immutable_track["the_immutable_var"]
    actual = schema.get("the_immutable_var")
    assert actual == expected

def test_get_immutable_specified_type(immutable_track, schema):
    expected = immutable_track["the_immutable_var"]
    actual = schema.get("the_immutable_var", track_type=TrackType.IMMUTABLE)
    assert actual == expected

def test_get_immutable_none(schema):
    actual = schema.get("doesn't exist", track_type=TrackType.IMMUTABLE)
    assert actual is None

def test_get_temporal(temporal_track, schema):
    expected = temporal_track["the_temporal_var"]
    actual = schema.get("the_temporal_var")
    assert actual == expected

def test_get_temporal_specified_type(temporal_track, schema):
    expected = temporal_track["the_temporal_var"]
    actual = schema.get("the_temporal_var", track_type=TrackType.TEMPORAL)
    assert actual == expected

def test_get_temporal_none(schema):
    actual = schema.get("doesn't exist", track_type=TrackType.TEMPORAL)
    assert actual is None

def test_get_immutable_wrong_type_raises(schema):
    with pytest.raises(ValueError):
        schema.get("the_temporal_var", track_type=TrackType.IMMUTABLE)

def test_get_temporal_wrong_type_raises(schema):
    with pytest.raises(ValueError):
        schema.get("the_immutable_var", track_type=TrackType.TEMPORAL)

def test_var_id_conflict_raises():
    t_spec: Dict = {
        "A": {
            "name": "temporal variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    i_spec: Dict = {
        "A": {
            "name": "immutable variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    t_track = Track.build(t_spec, None, "temporal")
    i_track = Track.build(i_spec, None, "immutable")
    with pytest.raises(ValueError):
        Schema(t_track, i_track)

def test_var_path_conflict_raises():
    t_spec: Dict = {
        "A": {
            "name": "variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    i_spec: Dict = {
        "B": {
            "name": "variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    t_track = Track.build(t_spec, None, "temporal")
    i_track = Track.build(i_spec, None, "immutable")
    with pytest.raises(DuplicatePathError):
        Schema(t_track, i_track)

@pytest.mark.parametrize("var_id, expected", [
    ("the_temporal_var", True),
    ("the_immutable_var", False)
])
def test_is_temporal(var_id, expected, schema):
    assert schema.is_temporal(var_id) is expected

def test_is_temporal_unknown_raises(schema):
    with pytest.raises(ValueError):
        schema.is_temporal("not a real variable")
