from typing import Dict, Set, List, cast
from unittest.mock import MagicMock

import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable, VariableId, Integer

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

def test_tree_with_metadata():
    metadata: Dict = {
        "foo": "bar",
        "a": "b"
    }
    var: Variable = Integer(track=MagicMock(), var_id=cast(VariableId, "target_var_2"), name="second_target",
                             sort_order=0, metadata=metadata, sources=[])
    expected: Dict = {
        "title": "second_target",
        "varId": "target_var_2",
        "dataType": "Integer",
        "metadata": metadata
    }
    actual: Dict = var.tree
    assert expected == actual

def test_tree_with_sources():
    sources: List[VariableId] = [cast(VariableId, x) for x in ("abc", "xyz")]
    var: Variable = Integer(track=MagicMock(), var_id=cast(VariableId, "target_var_2"), name="second_target",
                             sort_order=0, sources=sources)
    expected: Dict = {
        "title": "second_target",
        "varId": "target_var_2",
        "dataType": "Integer",
        "sources": sources
    }
    actual: Dict = var.tree
    assert expected == actual

def test_tree_from_source_folder_1(source_nested_dict_track):
    """Demonstrate what the tree looks like with children."""
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
    expected: Set[str] = {"outer_s", "initially_empty_folder"}
    actual: Set[str] = {v.name for v in track.roots}
    assert expected == actual

def test_absolute_path_keyed_list(target_list_track):
    var: Variable = target_list_track["target_keyed_list_color"]
    expected: List[str] = ["outer", "inner", "the_keyed_list", "color"]
    actual: List[str] = list(var.absolute_path)
    assert actual == expected

def test_relative_path_keyed_list(target_list_track):
    var: Variable = target_list_track["target_keyed_list_color"]
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

