import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable

def test_change_sort_order_does_not_affect_path(source_named_list_track):
    """Changing a variable's sort order does not affect its path."""
    track: Track = source_named_list_track
    var: Variable = track["source_root_1_ice_cream"]
    assert list(var.absolute_path) == ["list_source_1", "ice cream"]
    track.move("source_root_1_ice_cream", "source_root_1", 0)
    assert list(var.absolute_path) == ["list_source_1", "ice cream"]

def test_change_sort_order_does_not_affect_parent(source_named_list_track):
    """Changing a variable's sort order does not change the parent's "children" property."""
    track: Track = source_named_list_track
    var: Variable = track["source_root_1_ice_cream"]
    assert var.parent == "source_root_1"
    track.move("source_root_1_ice_cream", "source_root_1", 0)
    assert var.parent == "source_root_1"

def test_change_sort_order_alters_dict(source_named_list_track):
    """changing a variable's sort_order alters its json representation."""
    track: Track = source_named_list_track
    var: Variable = track["source_root_1_ice_cream"]
    track.move("source_root_1_ice_cream", "source_root_1", 0)
    assert var.dump() == {
        "name": "ice cream",
        "data_type": "Text",
        "parent": "source_root_1",
        "sort_order": 0
    }

def test_sort_order_before_pushes_down(source_named_list_track):
    """Placing a variable before other variables pushes all those other variables down."""
    track: Track = source_named_list_track
    track.move("source_root_1_ice_cream", "source_root_1", 0)
    assert track["source_root_1_name"].sort_order == 1
    assert track["source_root_1_age"].sort_order == 2

def test_sort_order_after_pulls_up(source_named_list_track):
    """Placing a variable after other variables pulls all those other variables up."""
    track: Track = source_named_list_track
    track.move("source_root_1_name", "source_root_1", 3)
    assert track["source_root_1_age"].sort_order == 0
    assert track["source_root_1_ice_cream"].sort_order == 1

def test_change_sort_order_alters_tree(source_named_list_track):
    """changing a variable's sort_order alters the tree from the sort_order onward."""
    track: Track = source_named_list_track
    track.move("source_root_1_ice_cream", "source_root_1", 0)
    root_var: Variable = track["source_root_1"]
    assert root_var.tree == {
        "title": "list_source_1",
        "varId": "source_root_1",
        "dataType": "NamedList",
        "children": [
            {
                "title": "ice cream",
                "varId": "source_root_1_ice_cream",
                "dataType": "Text"
            },
            {
                "title": "name",
                "varId": "source_root_1_name",
                "dataType": "Text"
            },
            {
                "title": "age",
                "varId": "source_root_1_age",
                "dataType": "Integer"
            },
            {
                "title": "sport",
                "varId": "source_root_1_sport",
                "dataType": "Text"
            }
        ]
    }

def test_negative_sort_order_raises(source_named_list_track):
    """Setting a sort order below zero is illegal."""
    track: Track = source_named_list_track
    with pytest.raises(ValueError):
        track.move("source_root_1_name", "source_root_1", -1)

def test_sort_order_gt_num_vars_raises(source_named_list_track):
    """Setting a sort order higher than the highest variable index is illegal."""
    track: Track = source_named_list_track
    with pytest.raises(ValueError):
        track.move("source_root_1_name", "source_root_1", 4)
