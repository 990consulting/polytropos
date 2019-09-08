import copy
from typing import List, Dict, cast, Iterator

import pytest

from polytropos.actions.filter import Filter
from polytropos.actions.filter.firstlast import EarliestFilter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.ontology.composite import Composite

import polytropos.ontology.schema
from polytropos.ontology.track import Track
from examples.s_8_filter_narrow.conf.filters.threshold import ImmutableValueThreshold
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def schema() -> polytropos.ontology.schema.Schema:
    temporal_spec: Dict = {
        "temporal_var": {
            "name": "t",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    temporal_track: Track = Track.build(temporal_spec, None, "temporal")

    immutable_spec: Dict = {
        "immutable_var": {
            "name": "i",
            "data_type": "Integer",
            "sort_order": 0
        }
    }
    immutable_track: Track = Track.build(immutable_spec, None, "immutable")
    return polytropos.ontology.schema.Schema(temporal_track, immutable_track)

@pytest.fixture()
def composite_1(schema) -> Composite:
    content: Dict = {
        "1": {"t": "a"},
        "2": {"t": "b"},
        "immutable": {"i": 74}
    }
    return Composite(schema, content)

@pytest.fixture()
def composite_2(schema) -> Composite:
    content: Dict = {
        "1": {"t": "x"},
        "2": {"t": "y"},
        "immutable": {"i": 1}
    }
    return Composite(schema, content)

@pytest.fixture()
def composites(composite_1, composite_2) -> List[Composite]:
    return [composite_1, composite_2]

@pytest.fixture()
def subject(schema) -> InMemoryFilterIterator:
    filters: List[Filter] = [
        ImmutableValueThreshold(schema, cast(VariableId, "immutable_var"), 7),
        EarliestFilter(schema)
    ]
    return InMemoryFilterIterator(filters)

def test_in_memory_filter(composites, subject, schema):
    expected: List = [
        Composite(schema, {
            "1": {"t": "a"},
            "immutable": {"i": 74}
        })
    ]
    actual: List = list(subject(composites))
    assert actual == expected

def test_in_memory_filter_output_is_a_copy(composites, subject):
    expected: Dict = copy.deepcopy(composites[0].content)
    list(subject(composites))
    actual: Dict = composites[0].content
    assert actual == expected
