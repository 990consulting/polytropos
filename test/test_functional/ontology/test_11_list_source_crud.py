import pytest
from polytropos.ontology.track import Track
from typing import Dict
import copy

def test_add_root_source(target_list_track):
    target_track: Track = target_list_track
    source_track: Track = target_track.source
    new_source_spec: Dict = {
        "name": "the_new_root_source",
        "data_type": "List",
        "sort_order": 0
    }
    source_track.add(new_source_spec, "A")
    target_list_track["target_list"].sources = ["source_list", "A"]
    assert target_track["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
        "sources": ["source_list", "A"]
    }

def test_add_root_source_does_not_affect_children(target_list_track):
    target_track: Track = target_list_track
    expected: Dict = copy.deepcopy(target_track["target_list_name"].dump())
    source_track: Track = target_track.source
    new_source_spec: Dict = {
        "name": "the_new_root_source",
        "data_type": "List",
        "sort_order": 0
    }
    source_track.add(new_source_spec, "A")
    target_list_track["target_list"].sources = ["source_list", "A"]
    actual: Dict = target_track["target_list_name"].dump()
    assert expected == actual

def test_delete_root_source_cascades(target_list_track):
    """When deleting a root source, child sources that descend from that root source should also be deleted."""
    target_list_track["target_list"].sources = []
    expected: Dict = {
        "name": "name",
        "data_type": "Text",
        "parent": "target_list",
        "sort_order": 0
    }
    actual: Dict = target_list_track["target_list_name"].dump()
    assert expected == actual

"""
def test_add_child_source_not_descended_from_root_source_raises(target_list_track):
    with pytest.raises(ValueError):
        target_list_track["target_list_name"].sources = ["source_list_name", "random_text_field"]
"""

"""
def test_add_nonexistent_child_source_raises(target_list_track):
    with pytest.raises(KeyError):
        target_list_track["target_list_name"].sources = ["source_list_name", "not_a_thing"]
"""

"""
def test_add_out_of_scope_child_raises(target_nested_list_track):
    with pytest.raises(ValueError):
        target_nested_list_track["name_id"].sources = ["name_1_id", "name_2_id", "descended_from_outer_list"]
"""
