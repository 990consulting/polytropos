from typing import Dict, Set, List

import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

def test_targets_for_var_in(target_nested_dict_track):
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source
    actual: Set[str] = set(source_track["source_var_2"].targets())
    expected: Set[str] = {"target_var_2"}
    assert actual == expected

def test_has_targets(target_nested_dict_track):
    source_track = target_nested_dict_track.source
    source_var: Variable = source_track["source_var_2"]
    assert source_var.has_targets

def test_get_children_no_parents(target_nested_dict_track):
    source_track = target_nested_dict_track.source
    source_var: Variable = source_track["source_folder_3"]
    assert [] == list(source_var.children)

def test_tree_from_target_var_2(target_nested_dict_track):
    """The tree takes a particular format intended for consumption by a particular React component. Only a few of the
    properties variable properties are included. The format is demonstrated here."""

    var: Variable = target_nested_dict_track["target_var_2"]
    expected: Dict = {
        "title": "second_target",
        "varId": "target_var_2",
        "dataType": "Integer"
    }
    actual: Dict = var.tree
    assert expected == actual

def test_tree_from_source_folder_1(source_nested_dict_track):
    var: Variable = source_nested_dict_track["source_folder_1"]
    expected: Dict = {
        "title": "outer_s",
        "varId": "source_folder_1",
        "dataType": "Folder",
        "children": [
            {
                "title": "first_source",
                "varId": "source_var_1",
                "dataType": "Integer"
            },
            {
                "title": "inner_s",
                "varId": "source_folder_2",
                "dataType": "Folder",
                "children": [
                    {
                        "title": "second_source",
                        "varId": "source_var_2",
                        "dataType": "Integer"
                    },
                    {
                        "title": "third_source",
                        "varId": "source_var_3",
                        "dataType": "Integer"
                    }
                ]
            }
        ]
    }
    actual: Dict = var.tree
    assert expected == actual

def test_track_roots(source_nested_dict_track):
    track: Track = source_nested_dict_track
    track.delete("source_folder_3")
    expected: Set[str] = {"outer_s"}
    actual: Set[str] = {v.name for v in track.roots}
    assert expected == actual

def test_absolute_path_named_list(target_list_track):
    var: Variable = target_list_track["target_named_list_color"]
    expected: List[str] = ["outer", "inner", "the_named_list", "color"]
    actual: List[str] = list(var.absolute_path)
    assert actual == expected

def test_relative_path_named_list(target_list_track):
    var: Variable = target_list_track["target_named_list_color"]
    expected: List[str] = ["color"]
    actual: List[str] = list(var.relative_path)
    assert actual == expected

def test_absolute_path_folder(simple_track):
    var: Variable = simple_track["target_var_id"]
    assert list(var.absolute_path) == ["the_folder", "the_target"]

def test_relative_path_folder(simple_track):
    var: Variable = simple_track["target_var_id"]
    assert list(var.relative_path) == ["the_folder", "the_target"]

def test_absolute_path_list(target_list_track):
    var: Variable = target_list_track["target_list_color"]
    assert list(var.absolute_path) == ["outer", "the_list", "color"]

def test_relative_path_list(target_list_track):
    var: Variable = target_list_track["target_list_color"]
    assert list(var.relative_path) == ["color"]

