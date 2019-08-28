from typing import Dict, Callable, List as ListType, Optional

import pytest

from polytropos.ontology.schema import Schema, TrackType
from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

@pytest.fixture
def half_spec() -> Callable:
    def _half_spec(cardinal: int, ordinal: str, prefix: str, track_name: str) -> Dict:
        return {
            "%s_folder_%i" % (prefix, cardinal): {
                "name": "%s_%s_folder" % (ordinal, track_name),
                "data_type": "Folder",
                "sort_order": 0
            },
            "%s_folder_text_%i" % (prefix, cardinal): {
                "name": "some_text",
                "data_type": "Text",
                "parent": "%s_folder_%i" % (prefix, cardinal),
                "sort_order": 0
            },
            "%s_list_%i" % (prefix, cardinal): {
                "name": "a_list",
                "data_type": "List",
                "parent": "%s_folder_%i" % (prefix, cardinal),
                "sort_order": 1
            },
            "%s_list_text_%i" % (prefix, cardinal): {
                "name": "some_text",
                "data_type": "Text",
                "parent": "%s_list_%i" % (prefix, cardinal),
                "sort_order": 0
            },
            "%s_named_list_%i" % (prefix, cardinal): {
                "name": "a_named_list",
                "data_type": "NamedList",
                "parent": "%s_list_%i" % (prefix, cardinal),
                "sort_order": 1
            },
            "%s_named_list_text_%i" % (prefix, cardinal): {
                "name": "some_text",
                "data_type": "Text",
                "parent": "%s_named_list_%i" % (prefix, cardinal),
                "sort_order": 0
            }
        }
    return _half_spec

@pytest.fixture
def track(half_spec) -> Callable:
    def _track(prefix, track_name) -> Track:
        first_half: Dict = half_spec(1, "first", prefix, track_name)
        second_half: Dict = half_spec(2, "second", prefix, track_name)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track

@pytest.fixture
def schema(track) -> Schema:
    temporal: Track = track("t", "temporal")
    immutable: Track = track("i", "immutable")
    return Schema(temporal, immutable)

# We test this exhaustively both for thoroughness and to measure performance
@pytest.mark.parametrize("abs_path, var_id", [
    (["first_temporal_folder"], "t_folder_1"),
    (["first_temporal_folder", "some_text"], "t_folder_text_1"),
    (["first_temporal_folder", "a_list"], "t_list_1"),
    (["first_temporal_folder", "a_list", "some_text"], "t_list_text_1"),
    (["first_temporal_folder", "a_list", "a_named_list"], "t_named_list_1"),
    (["first_temporal_folder", "a_list", "a_named_list", "some_text"], "t_named_list_text_1"),
    (["second_temporal_folder"], "t_folder_2"),
    (["second_temporal_folder", "some_text"], "t_folder_text_2"),
    (["second_temporal_folder", "a_list"], "t_list_2"),
    (["second_temporal_folder", "a_list", "some_text"], "t_list_text_2"),
    (["second_temporal_folder", "a_list", "a_named_list"], "t_named_list_2"),
    (["second_temporal_folder", "a_list", "a_named_list", "some_text"], "t_named_list_text_2"),
    (["first_immutable_folder"], "i_folder_1"),
    (["first_immutable_folder", "some_text"], "i_folder_text_1"),
    (["first_immutable_folder", "a_list"], "i_list_1"),
    (["first_immutable_folder", "a_list", "some_text"], "i_list_text_1"),
    (["first_immutable_folder", "a_list", "a_named_list"], "i_named_list_1"),
    (["first_immutable_folder", "a_list", "a_named_list", "some_text"], "i_named_list_text_1"),
    (["second_immutable_folder"], "i_folder_2"),
    (["second_immutable_folder", "some_text"], "i_folder_text_2"),
    (["second_immutable_folder", "a_list"], "i_list_2"),
    (["second_immutable_folder", "a_list", "some_text"], "i_list_text_2"),
    (["second_immutable_folder", "a_list", "a_named_list"], "i_named_list_2"),
    (["second_immutable_folder", "a_list", "a_named_list", "some_text"], "i_named_list_text_2")
])
def test_lookup_initial(schema: Schema, abs_path: ListType[str], var_id: str):
    """Verifying that lookup works as expected off the bat."""
    expected: Variable = schema.get(var_id)
    assert expected is not None
    actual: Variable = schema.lookup(abs_path)
    assert actual is expected
