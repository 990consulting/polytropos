import copy
from typing import Dict

import pytest

from polytropos.ontology.schema import Schema, TrackType
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
    expected = immutable_track.variables["the_immutable_var"]
    actual = schema.get("the_immutable_var")
    assert actual == expected

def test_get_immutable_specified_type(immutable_track, schema):
    expected = immutable_track.variables["the_immutable_var"]
    actual = schema.get("the_immutable_var", track_type=TrackType.IMMUTABLE)
    assert actual == expected

def test_get_immutable_none(schema):
    actual = schema.get("doesn't exist", track_type=TrackType.IMMUTABLE)
    assert actual is None

def test_get_temporal(temporal_track, schema):
    expected = temporal_track.variables["the_temporal_var"]
    actual = schema.get("the_temporal_var")
    assert actual == expected

def test_get_temporal_specified_type(temporal_track, schema):
    expected = temporal_track.variables["the_temporal_var"]
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

@pytest.mark.parametrize("track_type", list(TrackType))
def test_get_conflict_raises(track_type):
    t_spec: Dict = {
        "A": {
            "name": "temporal variable",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    t_track = Track.build(t_spec, None, "temporal")
    i_spec = copy.deepcopy(t_spec)
    i_track = Track.build(i_spec, None, "immutable")
    schema = Schema(t_track, i_track)
    with pytest.raises(ValueError):
        schema.get("A", track_type=track_type)
