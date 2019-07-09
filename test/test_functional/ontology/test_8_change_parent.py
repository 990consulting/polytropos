from typing import Dict, List

import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable


def children_to_set(children):
    return set(child.var_id for child in children)


# TODO In order for this to work, the setter for the parent property may need to make a callback to the track to
#  update its internal state.
def test_change_parent_alters_relative_path(target_list_track):
    """moving a variable to a new parent changes its relative path."""
    var: Variable = target_list_track["target_named_list_color"]
    new_folder_spec: Dict = {
        "name": "a_new_folder",
        "parent": "target_named_list",
        "data_type": "Folder",
        "sort_order": 0
    }

    target_list_track.add(new_folder_spec, "new_nested_folder")
    target_list_track.move("target_named_list_color", "new_nested_folder", 0)
    expected: List[str] = ["a_new_folder", "color"]
    actual: List[str] = list(var.relative_path)
    assert actual == expected

def test_change_parent_alters_absolute_path(target_list_track):
    """moving a variable to a new parent changes its absolute path."""
    var: Variable = target_list_track["target_named_list_color"]
    new_folder_spec: Dict = {
        "name": "a_new_folder",
        "parent": "target_named_list",
        "data_type": "Folder",
        "sort_order": 0
    }

    target_list_track.add(new_folder_spec, "new_nested_folder")
    target_list_track.move("target_named_list_color", "new_nested_folder", 0)
    expected: List[str] = ["outer", "inner", "the_named_list", "a_new_folder", "color"]
    actual: List[str] = list(var.absolute_path)
    assert actual == expected

def test_change_parent_alters_original_parent_children(source_nested_dict_track):
    assert children_to_set(source_nested_dict_track["source_folder_1"].children) == {"source_var_1", "source_folder_2"}
    source_nested_dict_track.move("source_var_1", "source_folder_3", 0)
    assert children_to_set(source_nested_dict_track["source_folder_1"].children) == {"source_folder_2"}

def test_change_parent_alters_new_parent_children(source_nested_dict_track):
    assert children_to_set(source_nested_dict_track["source_folder_3"].children) == set()
    source_nested_dict_track.move("source_var_1", "source_folder_3", 0)
    assert children_to_set(source_nested_dict_track["source_folder_3"].children) == {"source_var_1"}

def test_change_parent_alters_original_descendants_that(source_nested_dict_track):
    """after changing the parent, the original parent no longer includes the node in descendents_that()."""
    original_root: Variable = source_nested_dict_track["source_folder_1"]
    assert set(original_root.descendants_that()) == {"source_var_1", "source_folder_2", "source_var_2", "source_var_3"}
    source_nested_dict_track.move("source_var_3", "source_folder_3", 0)
    assert set(original_root.descendants_that()) == {"source_var_1", "source_folder_2", "source_var_2"}

def test_change_parent_alters_new_descendants_that(source_nested_dict_track):
    """after changing the parent, the new parent includes the node in descendents_that()."""
    new_root: Variable = source_nested_dict_track["source_folder_3"]
    assert set(new_root.descendants_that()) == set()
    source_nested_dict_track.move("source_var_3", "source_folder_3", 0)
    assert set(new_root.descendants_that()) == {"source_var_3"}

def test_move_updates_sort_order(simple_track):
    """In simple_spec, target_folder is on the same level as target_var_id. After moving the latter inside the former,
    the sort order of target_folder should move down because target_var_id is no longer above it."""
    simple_track.move("target_var_id", "target_folder", 0)
    expected: Dict = {
        "target_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_var_id": {
            "name": "the_target",
            "data_type": "Integer",
            "parent": "target_folder",
            "sort_order": 0
        }
    }
    actual: Dict = simple_track.dump()
    assert actual == expected

def test_move_to_root(source_nested_dict_track):
    source_nested_dict_track.move("source_var_2", None, 0)
    expected: Dict = {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder_1",
            "sort_order": 0
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "sort_order": 0
        },
        "source_folder_1": {
            "name": "outer_s",
            "data_type": "Folder",
            "sort_order": 1   # Got pushed down by source_var_2
        },
        "source_folder_2": {
            "name": "inner_s",
            "data_type": "Folder",
            "parent": "source_folder_1",
            "sort_order": 1
        },
        "source_var_3": {
            "name": "third_source",
            "data_type": "Integer",
            "parent": "source_folder_2",
            "sort_order": 0   # Got pushed up by source_var_2 going away
        },
        "source_folder_3": {
            "name": "initially_empty_folder",
            "data_type": "Folder",
            "sort_order": 2   # Got pushed down by source_folder_1, which was pushed down by source_var_2
        }
    }
    actual: Dict = source_nested_dict_track.dump()
    assert actual == expected

def test_move_list_descendent_out_of_list_raises(target_list_track):
    with pytest.raises(ValueError):
        target_list_track.move("target_named_list_color", None, 0)

def test_move_non_list_descendent_into_list_raises(target_list_track):
    new_var_spec: Dict = {
        "name": "Not inside of any list",
        "data_type": "Integer",
        "sort_order": 0
    }
    target_list_track.add(new_var_spec, "new_var")

    with pytest.raises(ValueError):
        target_list_track.move("new_var", "target_list", 0)

def test_move_parent_inside_child_raises(source_nested_dict_track):
    track: Track = source_nested_dict_track
    with pytest.raises(ValueError):
        track.move("source_folder_1", "source_folder_2", 0)

def test_change_parent_does_not_affect_source_status(target_nested_dict_track):
    """moving a variable does not alter its status as a source."""
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source

    assert set(target_track["target_var_1"].sources) == {"source_var_1"}
    source_track.move("source_var_1", None, 0)
    assert set(target_track["target_var_1"].sources) == {"source_var_1"}

def test_change_parent_does_not_affect_target_status(target_nested_dict_track):
    """moving a variable does not alter its status as a target."""
    target_track: Track = target_nested_dict_track
    source_track: Track = target_track.source

    assert set(source_track["source_var_1"].targets()) == {"target_var_1"}
    target_track.move("target_var_1", None, 0)
    assert set(source_track["source_var_1"].targets()) == {"target_var_1"}

def test_change_parent_alters_dict(simple_track):
    """changing a variable's parent alters its dictionary representation."""
    simple_track.move("target_var_id", "target_folder", 0)
    expected: Dict = {
        "name": "the_target",
        "data_type": "Integer",
        "parent": "target_folder",
        "sort_order": 0
    }
    actual: Dict = simple_track["target_var_id"].dump()
    assert actual == expected

def test_change_parent_alters_tree(simple_track):
    """changing a variable's parent alters the tree from the parent onward."""
    simple_track.move("target_var_id", "target_folder", 0)
    expected: Dict = {
        "title": "the_folder",
        "varId": "target_folder",
        "dataType": "Folder",
        "children": [
            {
                "title": "the_target",
                "varId": "target_var_id",
                "dataType": "Integer"
            }
        ]
    }
    actual: Dict = simple_track["target_folder"].tree
    assert actual == expected

def test_move_to_non_container_raises(simple_track):
    with pytest.raises(ValueError):
        simple_track.move("target_folder", "target_var_id", 0)

def test_move_to_nonexistent_parent_raises(simple_track):
    with pytest.raises(ValueError):
        simple_track.move("target_var_id", "something that doesn't exist", 0)

def test_add_parent_removes_from_root_list(simple_flat_track):
    assert {v.var_id for v in simple_flat_track.roots} == {"target_folder", "target_var_id"}
    simple_flat_track.move("target_var_id", "target_folder", 0)
    assert {v.var_id for v in simple_flat_track.roots} == {"target_folder"}

def test_remove_parent_adds_to_root_list(source_nested_dict_track):
    track: Track = source_nested_dict_track
    assert {v.var_id for v in track.roots} == {"source_folder_1", "source_folder_3"}
    source_nested_dict_track.move("source_var_2", None, 0)
    assert {v.var_id for v in track.roots} == {"source_folder_1", "source_folder_3", "source_var_2"}
