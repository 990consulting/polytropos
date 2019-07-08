from typing import Dict, Set

import pytest

from polytropos.ontology.track import Track

def test_delete_var_with_children_raises(source_nested_dict_track):
    track: Track = source_nested_dict_track

    with pytest.raises(ValueError):
        track.delete("source_folder_1")

def test_delete_var_with_targets_raises(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    track: Track = target_track.source

    with pytest.raises(ValueError):
        track.delete("source_var_2")

def test_delete_updates_track_index(source_nested_dict_track):
    track: Track = source_nested_dict_track
    assert "source_var_3" in track
    track.delete("source_var_3")
    assert "source_var_3" not in track

def test_delete_updates_parent_tree(source_nested_dict_track):
    track: Track = source_nested_dict_track
    track.delete("source_var_3")
    expected: Dict = {
        "title": "inner_s",
        "varId": "source_folder_2",
        "dataType": "Folder",
        "children": [
            {
                "title": "second_source",
                "varId": "source_var_2",
                "dataType": "Integer"
            }
        ]
    }
    actual: Dict = track["source_folder_2"].tree
    assert expected == actual

def test_delete_updates_local_sort_order(source_nested_dict_track):
    track: Track = source_nested_dict_track
    track.delete("source_var_2")
    assert track["source_var_3"].sort_order == 0

def test_delete_root_updates_track_roots(source_nested_dict_track):
    track: Track = source_nested_dict_track
    track.delete("source_folder_3")
    expected: Set[str] = {"outer_s"}
    actual: Set[str] = {v.name for v in track.roots}
    assert expected == actual

def test_delete_updates_source_for_vars_in(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    target_track.delete("target_var_2")
    actual: Set[str] = set(source_track["source_var_2"].targets())
    expected: Set[str] = set()
    assert actual == expected

def test_delete_updates_has_targets_for_source(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    assert source_track["source_var_2"].has_targets
    target_track.delete("target_var_2")
    assert not source_track["source_var_2"].has_targets

def test_delete_updates_descendants_that(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    target_track.delete("target_var_2")
    expected: Set[str] = {"source_var_1"}
    actual: Set[str] = set(source_track.descendants_that(container=-1, targets=1))
    assert expected == actual

def test_delete_changes_track_dump(target_nested_dict_track):
    track: Track = target_nested_dict_track
    track.delete("target_var_2")
    expected: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "parent": "target_folder_1",
            "sort_order": 0
        },
        "target_folder_1": {
            "name": "outer_s",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_folder_2": {
            "name": "inner_s",
            "data_type": "Folder",
            "parent": "target_folder_1",
            "sort_order": 1
        }
    }
    actual: Dict = track.dump()
    assert expected == actual
