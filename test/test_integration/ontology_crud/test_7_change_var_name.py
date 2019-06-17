import copy
from typing import Dict, List

import pytest

from polytropos.ontology.variable import Variable

def test_change_name_alters_variable_dict(simple_track, simple_spec):
    var: Variable = simple_track["target_var_id"]
    var.name = "Sir Robert"

    expected: Dict = {
        "name": "Sir Robert",
        "data_type": "Integer",
        "sort_order": 0,
        "parent": "target_folder"
    }

    actual = var.dump()
    assert actual == expected

def test_change_name_alters_track_list(simple_track, simple_spec):
    expected: Dict = copy.deepcopy(simple_spec)
    expected["target_var_id"]["name"] = "Sir Robert"

    var: Variable = simple_track["target_var_id"]
    var.name = "Sir Robert"

    actual: Dict = simple_track.dump()
    assert actual == expected

def test_change_name_alters_absolute_path(target_list_track):
    var: Variable = target_list_track["target_named_list_color"]
    var.name = "Sir Robert"
    expected: List[str] = ["outer", "inner", "the_named_list", "Sir Robert"]
    actual: List[str] = list(var.absolute_path)
    assert actual == expected

def test_change_name_alters_relative_path(target_list_track):
    var: Variable = target_list_track["target_named_list_color"]
    var.name = "Sir Robert"
    expected: List[str] = ["Sir Robert"]
    actual: List[str] = list(var.relative_path)
    assert actual == expected

def test_change_name_alters_tree(source_nested_dict_track):
    var: Variable = source_nested_dict_track["source_var_2"]
    var.name = "Sir Robert"
    folder = source_nested_dict_track["source_folder_2"]
    folder.name = "Bravely Ran Away"
    expected: Dict = {
        "title": "Bravely Ran Away",
        "varId": "source_folder_2",
        "dataType": "Folder",
        "children": [
            {
                "title": "Sir Robert",
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
    actual: Dict = folder.tree
    assert actual == expected

def test_set_locally_non_unique_name_raises(source_nested_dict_track):
    var: Variable = source_nested_dict_track["source_var_2"]

    with pytest.raises(ValueError):
        var.name = "third_source"

@pytest.mark.parametrize("illegal_name", ["/I have a slash", "I.Have.Periods"])
def test_set_illegal_name_raises(source_nested_dict_track, illegal_name):
    var: Variable = source_nested_dict_track["source_var_2"]
    with pytest.raises(ValueError):
        var.name = illegal_name
