import copy
from typing import Dict, List, Callable

import pytest

from polytropos.util import schemas

@pytest.fixture()
def do_test() -> Callable:
    def _do_test(existing: Dict, path: List[str], expected_spec: str, expected_var_id: str) -> None:
        target: Dict = copy.deepcopy(existing)
        actual_var_id: str = schemas.build_folders(target, path, "the_prefix_")
        assert actual_var_id == expected_var_id
        assert target == expected_spec
    return _do_test

def test_one_level_content(do_test):
    existing: Dict = {}
    path: List[str] = ["the_only"]
    expected_spec: Dict = {
        "the_prefix_the_only": {
            "name": "the_only",
            "data_type": "Folder"
        }
    }
    expected_var_id: str = "the_prefix_the_only"
    do_test(existing, path, expected_spec, expected_var_id)

def test_one_level_content_already_exists(do_test):
    existing: Dict = {
        "the_prefix_the_only": {
            "name": "the_only",
            "data_type": "Folder"
        }
    }
    path: List[str] = ["the_only"]
    expected_spec: Dict = copy.deepcopy(existing)
    expected_var_id: str = "the_prefix_the_only"
    do_test(existing, path, expected_spec, expected_var_id)

def test_three_levels(do_test):
    existing: Dict = {}
    path: List[str] = ["x", "y", "z"]
    expected_var_id: str = "the_prefix_x_y_z"
    expected_spec: Dict = {
        "the_prefix_x": {
            "name": "x",
            "data_type": "Folder"
        },
        "the_prefix_x_y": {
            "name": "y",
            "data_type": "Folder",
            "parent_id": "the_prefix_x"
        },
        "the_prefix_x_y_z": {
            "name": "z",
            "data_type": "Folder",
            "parent_id": "the_prefix_x_y"
        }
    }
    do_test(existing, path, expected_spec, expected_var_id)

def test_three_levels_two_exist_one_is_a_list(do_test):
    existing: Dict = {
        "the_prefix_x": {
            "name": "x",
            "data_type": "Folder"
        },
        "the_prefix_x_y": {
            "name": "y",
            "data_type": "List",
            "parent_id": "the_prefix_x"
        }
    }
    expected_spec: Dict = {
        "the_prefix_x": {
            "name": "x",
            "data_type": "Folder"
        },
        "the_prefix_x_y": {
            "name": "y",
            "data_type": "List",
            "parent_id": "the_prefix_x"
        },
        "the_prefix_x_y_z": {
            "name": "z",
            "data_type": "Folder",
            "parent_id": "the_prefix_x_y"
        }
    }
    path: List[str] = ["x", "y", "z"]
    expected_var_id: str = "the_prefix_x_y_z"
    do_test(existing, path, expected_spec, expected_var_id)

def test_illegal_ancestor_raises(do_test):
    existing: Dict = {
        "the_prefix_x": {
            "name": "x",
            "data_type": "Folder"
        },
        "the_prefix_x_y": {
            "name": "y",
            "data_type": "Text",
            "parent_id": "the_prefix_x"
        }
    }
    path: List[str] = ["x", "y", "z"]
    with pytest.raises(AssertionError):
        schemas.build_folders(existing, path, "the_prefix_")
