from typing import Dict, Callable

import pytest

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture(scope="module")
def half_source_spec() -> Callable:
    def _half_source_spec(cardinal: int, ordinal: str, prefix: str, track_name: str) -> Dict:
        return {
            "source_%s_folder_%i" % (prefix, cardinal): {
                "name": "%s_%s_folder" % (ordinal, track_name),
                "data_type": "Folder",
                "sort_order": 0
            },
            "source_%s_folder_text_%i" % (prefix, cardinal): {
                "name": "some_text",
                "data_type": "Text",
                "parent": "source_%s_folder_%i" % (prefix, cardinal),
                "sort_order": 0
            },
            "source_%s_list_%i" % (prefix, cardinal): {
                "name": "a_list",
                "data_type": "List",
                "parent": "source_%s_folder_%i" % (prefix, cardinal),
                "sort_order": 1
            },
            "source_%s_list_text_%i" % (prefix, cardinal): {
                "name": "some_text",
                "data_type": "Text",
                "parent": "source_%s_list_%i" % (prefix, cardinal),
                "sort_order": 0
            },
            "source_%s_named_list_%i" % (prefix, cardinal): {
                "name": "a_named_list",
                "data_type": "NamedList",
                "parent": "source_%s_list_%i" % (prefix, cardinal),
                "sort_order": 1
            },
            "source_%s_named_list_text_%i" % (prefix, cardinal): {
                "name": "some_text",
                "data_type": "Text",
                "parent": "source_%s_named_list_%i" % (prefix, cardinal),
                "sort_order": 0
            }
        }
    return _half_source_spec

@pytest.fixture
def source_track(half_source_spec) -> Callable:
    def _track(prefix, track_name) -> Track:
        first_half: Dict = half_source_spec(1, "first", prefix, track_name)
        second_half: Dict = half_source_spec(2, "second", prefix, track_name)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track

@pytest.fixture
def source_schema(source_track) -> Schema:
    temporal: Track = source_track("t", "temporal")
    immutable: Track = source_track("i", "immutable")
    return Schema(temporal, immutable)


@pytest.fixture
def target_spec() -> Callable:
    def _target_spec(prefix: str, track_name: str) -> Dict:
        return {
            "target_%s_folder" % prefix: {
                "name": "%s_folder" % track_name,
                "data_type": "Folder",
                "sort_order": 0
            },
            "target_%s_folder_text" % prefix: {
                "name": "some_text",
                "data_type": "Text",
                "parent": "target_%s_folder" % prefix,
                "sort_order": 0,
                "sources": ["source_%s_folder_text_1" % prefix]  # Confirm support of variable length source lists
            },
            "target_%s_list" % prefix: {
                "name": "a_list",
                "data_type": "List",
                "parent": "target_%s_folder" % prefix,
                "sort_order": 1,
                "sources": ["source_%s_list_%i" % (prefix, x) for x in [1, 2]]
            },
            "target_%s_list_text" % prefix: {
                "name": "some_text",
                "data_type": "Text",
                "parent": "target_%s_list" % prefix,
                "sort_order": 0,
                "sources": ["source_%s_list_text_%i" % (prefix, x) for x in [1, 2]]
            },
            "target_%s_named_list" % prefix: {
                "name": "a_named_list",
                "data_type": "NamedList",
                "parent": "target_%s_list" % prefix,
                "sort_order": 1,
                "sources": ["source_%s_named_list_%i" % (prefix, x) for x in [1, 2]]
            },
            "target_%s_named_list_text" % prefix: {
                "name": "some_text",
                "data_type": "Text",
                "parent": "target_%s_named_list" % prefix,
                "sort_order": 0,
                "sources": ["source_%s_named_list_text_%i" % (prefix, x) for x in [1, 2]]
            }
        }
    return _target_spec

@pytest.fixture
def target_track(target_spec: Callable) -> Callable:
    def _track(prefix: str, track_name: str, source_track: Track) -> Track:
        spec: Dict = target_spec(prefix, track_name)
        return Track.build(spec, source_track, track_name)
    return _track

@pytest.fixture
def target_schema(source_schema, target_track) -> Schema:
    temporal: Track = target_track("t", "temporal", source_schema.temporal)
    immutable: Track = target_track("i", "immutable", source_schema.immutable)
    return Schema(temporal, immutable)