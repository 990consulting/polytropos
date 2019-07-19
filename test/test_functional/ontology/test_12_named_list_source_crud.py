import pytest
from polytropos.ontology.track import Track
from typing import Dict
import copy

def test_add_root_source(target_named_list_track):
    target_track: Track = target_named_list_track
    source_track: Track = target_track.source
    new_source_spec: Dict = {
        "name": "the_new_root_source",
        "data_type": "NamedList",
        "sort_order": 0
    }
    source_track.add(new_source_spec, "A")
    target_named_list_track["target_root"].sources = ["source_root_1", "source_root_2", "A"]
    assert target_track["target_root"].dump() == {
        "name": "People",
        "data_type": "NamedList",
        "sort_order": 0,
        "sources": ["source_root_1", "source_root_2", "A"]
    }

def test_add_root_source_does_not_affect_children(target_named_list_track):
    target_track: Track = target_named_list_track
    expected = copy.deepcopy(target_track["target_root_name"].dump())
    source_track: Track = target_track.source
    new_source_spec: Dict = {
        "name": "the_new_root_source",
        "data_type": "NamedList",
        "sort_order": 0
    }
    source_track.add(new_source_spec, "A")
    target_named_list_track["target_root"].sources = ["source_root_1", "source_root_2", "A"]
    actual: Dict = target_track["target_root_name"].dump()
    assert expected == actual

def test_delete_root_source_cascades(target_named_list_track):
    """When deleting a root source, child sources that descend from that root source should also be deleted."""
    target_named_list_track["target_root"].sources = []
    expected: Dict = {
        "name": "Name",
        "data_type": "Text",
        "sort_order": 0,
        "parent": "target_root"
    }
    actual: Dict = target_named_list_track["target_root_name"].dump()
    assert expected == actual

"""
def test_add_child_source_not_descended_from_root_source_raises(target_named_list_track):
    with pytest.raises(ValueError):
        target_named_list_track["target_root_name"].sources = ["source_root_1_name", "source_root_2_nombre",
                                                                         "random_text_field"]
"""

"""
def test_add_nonexistent_child_source_raises(target_named_list_track):
    with pytest.raises(KeyError):
        target_named_list_track["target_root_name"].sources = ["source_root_1_name", "source_root_2_nombre",
                                                                         "not_a_thing"]
"""

"""
def test_add_out_of_scope_child_raises(target_nested_list_track):
    with pytest.raises(ValueError):
        target_nested_list_track["name_id"].sources = ["name_1_id", "name_2_id", "descended_from_outer_list"]
"""
