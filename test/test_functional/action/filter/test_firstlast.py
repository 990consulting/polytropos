from typing import Dict

import pytest
from polytropos.ontology.composite import Composite
from polytropos.actions.filter.firstlast import EarliestFilter, LatestFilter

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture()
def schema() -> Schema:
    temporal_spec: Dict = {
        "some_field": {
            "data_type": "Text",
            "name": "key",
            "sort_order": 0
        }
    }
    temporal_track: Track = Track.build(temporal_spec, None, "temporal")
    immutable_track: Track = Track.build({}, None, "immutable")
    return Schema(temporal_track, immutable_track)

@pytest.fixture()
def composite(schema) -> Composite:
    content: Dict = {
        "1": {"key": "A"},
        "2": {"key": "B"},
        "3": {"key": "C"},
        "immutable": {"_should not touch this": None}
    }
    return Composite(schema, content)

def test_filter_earliest_passes(composite, schema):
    earliest_filter: EarliestFilter = EarliestFilter(schema)
    assert earliest_filter.passes(composite)

def test_filter_earliest(composite, schema):
    earliest_filter: EarliestFilter = EarliestFilter(schema)
    earliest_filter.narrow(composite)

    expected: Dict = {
        "1": {"key": "A"},
        "immutable": {"_should not touch this": None}
    }

    assert composite.content == expected

def test_filter_latest_passes(composite, schema):
    latest_filter: LatestFilter = LatestFilter(schema)
    assert latest_filter.passes(composite)

def test_filter_latest(composite, schema):
    latest_filter: LatestFilter = LatestFilter(schema)
    latest_filter.narrow(composite)

    expected: Dict = {
        "3": {"key": "C"},
        "immutable": {"_should not touch this": None}
    }

    assert composite.content == expected
