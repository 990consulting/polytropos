from typing import Dict

import pytest

from etl4.ontology.track import Track

def test_add_root_source(target_list_track):
    target_track: Track = target_list_track
    source_track: Track = target_track.source
    new_source_spec: Dict = {
        "name": "the_new_root_source",
        "data_type": "List",
        "sort_order": 0
    }
    source_track.add(new_source_spec, "A")
    target_list_track.variables["target_list"].sources = ["source_list", "A"]
    assert target_track.variables["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
        "sources": ["source_list", "A"],
        "source_child_mappings": {
            "source_list": {
                "target_list_name": ["source_list_name"],
                "target_list_color": ["source_list_color"]
            },
            "A": {
                "target_list_name": [],
                "target_list_color": []
            }
        }
    }

def test_delete_root_source(target_list_track):
    target_list_track.variables["target_list"].sources = []
    assert target_list_track.variables["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
    }

def test_add_child_source_mapping(target_list_track):
    target_list_track.variables["target_list_name"].alter_list_child_source_mappings("source_list", [
        "source_list_name",
        "source_list_color"
    ])
    assert target_list_track.variables["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
        "sources": ["source_list"],
        "source_child_mappings": {
            "source_list": {
                "target_list_name": ["source_list_name", "source_list_color"],
                "target_list_color": ["source_list_color"]
            }
        }
    }

def test_remove_child_source_mapping(target_list_track):
    target_list_track.variables["target_list_name"].alter_list_child_source_mappings("source_list", [])
    assert target_list_track.variables["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
        "sources": ["source_list"],
        "source_child_mappings": {
            "source_list": {
                "target_list_name": [],
                "target_list_color": ["source_list_color"]
            }
        }
    }

def test_alter_mapping_for_nonexistent_root_raises(target_list_track):
    with pytest.raises(ValueError):
        target_list_track.variables["target_list_name"].alter_list_child_source_mappings("not_a_real_root", [])

def test_add_child(target_list_track):
    new_list_child_spec: Dict = {
        "name": "the new list member",
        "data_type": "Text",
        "parent": "target_list",
        "sort_order": 0
    }
    target_list_track.add(new_list_child_spec, "A")
    assert target_list_track.variables["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
        "sources": ["source_list"],
        "source_child_mappings": {
            "source_list": {
                "target_list_name": ["source_list_name"],
                "target_list_color": ["source_list_color"],
                "A": []
            }
        }
    }

def test_remove_child_alters_child_source_mappings(target_list_track):
    target_list_track.delete("target_list_name")
    assert target_list_track.variables["target_list"].dump() == {
        "name": "the_list",
        "data_type": "List",
        "parent": "target_folder_outer",
        "sort_order": 1,
        "sources": ["source_list"],
        "source_child_mappings": {
            "source_list": {
                "target_list_color": ["source_list_color"]
            }
        }
    }
