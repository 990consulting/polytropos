from typing import Dict

import pytest

from etl4.ontology.track import Track

def test_add_root_source(target_named_list_track):
    target_track: Track = target_named_list_track
    source_track: Track = target_track.source
    new_source_spec: Dict = {
        "name": "the_new_root_source",
        "data_type": "NamedList",
        "sort_order": 0
    }
    source_track.add(new_source_spec, "A")
    target_named_list_track.variables["target_root"].sources = ["source_root_1", "source_root_2", "A"]
    assert target_track.variables["target_root"].dump() == {
        "name": "People",
        "data_type": "NamedList",
        "sources": ["source_root_1", "source_root_2", "A"],
        "sort_order": 0,
        "source_child_mappings": {
            "source_root_1": {
                "target_root_name": ["source_root_1_name"],
                "target_root_age": ["source_root_1_age"],
                "target_root_ice_cream": ["source_root_1_ice_cream"],
                "target_root_sport": ["source_root_1_sport"]
            },
            "source_root_2": {
                "target_root_name": ["source_root_2_nombre"],
                "target_root_age": ["source_root_2_edad"],
                "target_root_ice_cream": ["source_root_2_helado"],
                "target_root_sport": []
            },
            "A": {
                "target_root_name": [],
                "target_root_age": [],
                "target_root_ice_cream": [],
                "target_root_sport": []
            }
        }
    }

def test_delete_root_source(target_named_list_track):
    target_named_list_track.variables["target_root"].sources = ["source_root_1"]
    assert target_named_list_track.variables["target_root"].dump() == {
        "name": "People",
        "data_type": "NamedList",
        "sources": ["source_root_1"],
        "sort_order": 0,
        "source_child_mappings": {
            "source_root_1": {
                "target_root_name": ["source_root_1_name"],
                "target_root_age": ["source_root_1_age"],
                "target_root_ice_cream": ["source_root_1_ice_cream"],
                "target_root_sport": ["source_root_1_sport"]
            }
        }
    }

def test_add_child(target_named_list_track):
    new_list_child_spec: Dict = {
        "name": "the new list member",
        "data_type": "Text",
        "parent": "target_root",
        "sort_order": 0
    }
    target_named_list_track.add(new_list_child_spec, "A")
    assert target_named_list_track.variables["target_root"].dump() == {
        "name": "People",
        "data_type": "NamedList",
        "sources": ["source_root_1", "source_root_2"],
        "sort_order": 0,
        "source_child_mappings": {
            "source_root_1": {
                "target_root_name": ["source_root_1_name"],
                "target_root_age": ["source_root_1_age"],
                "target_root_ice_cream": ["source_root_1_ice_cream"],
                "target_root_sport": ["source_root_1_sport"],
                "A": []
            },
            "source_root_2": {
                "target_root_name": ["source_root_2_nombre"],
                "target_root_age": ["source_root_2_edad"],
                "target_root_ice_cream": ["source_root_2_helado"],
                "target_root_sport": [],
                "A": []
            }
        }
    }

def test_remove_child_alters_child_source_mappings(target_named_list_track):
    target_named_list_track.delete("target_root_name")
    assert target_named_list_track.variables["target_root"].dump() == {
        "name": "People",
        "data_type": "NamedList",
        "sources": ["source_root_1", "source_root_2"],
        "sort_order": 0,
        "source_child_mappings": {
            "source_root_1": {
                "target_root_age": ["source_root_1_age"],
                "target_root_ice_cream": ["source_root_1_ice_cream"],
                "target_root_sport": ["source_root_1_sport"]
            },
            "source_root_2": {
                "target_root_age": ["source_root_2_edad"],
                "target_root_ice_cream": ["source_root_2_helado"],
                "target_root_sport": []
            }
        }
    }
