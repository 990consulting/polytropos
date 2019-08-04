import pytest

from polytropos.actions.consume.tocsv.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.valueset import ValueSet
from typing import List, Tuple, Dict

@pytest.fixture()
def as_block_value(schema) -> AsBlockValue:
    return AsBlockValue(schema)

@pytest.fixture()
def common_values() -> Dict:
    return {
        "i_text_in_folder": "foo",
        "i_list_in_folder": [
            {
                "i_text_in_list_in_folder": "a"
            },
            {
                "i_text_in_list_in_folder": "b",
                "i_int_in_list_in_folder": 2
            },
            {
                "i_text_in_list_in_folder": "c",
                "i_int_in_list_in_folder": 3
            }
        ],
        "i_outer_nested_list": [
            {
                "i_text_in_outer_nested_list": "a"
            },
            {
                "i_text_in_outer_nested_list": "b",
                "i_inner_nested_list": [
                    {}
                ]
            },
            {
                "i_text_in_outer_nested_list": "c",
                "i_inner_nested_list": [
                    {
                        "i_text_in_inner_nested_list": "foo"
                    },
                    {
                        "i_text_in_inner_nested_list": "bar"
                    }
                ]
            }
        ],
        "i_named_list_in_root": {
            "peter": {
                "i_text_in_named_list": "a"
            },
            "paul": {
                "i_text_in_named_list": "b",
                "i_int_in_named_list": 2
            },
            "mary": {
                "i_text_in_named_list": "c",
                "i_int_in_named_list": 3
            }
        },
        "i_outer_nested_named_list": {
            "peter": {
                "i_text_in_outer_nested_named_list": "a"
            },
            "paul": {
                "i_text_in_outer_nested_named_list": "b",
                "i_inner_nested_named_list": {
                    "red": {}
                }
            },
            "mary": {
                "i_text_in_outer_nested_named_list": "c",
                "i_inner_nested_named_list": {
                    "orange": {
                        "i_text_in_inner_nested_named_list": "foo"
                    },
                    "yellow": {
                        "i_text_in_inner_nested_named_list": "bar"
                    }
                }
            }
        }
    }

def test_singleton(common_values, as_block_value):
    block: Tuple = ("i_text_in_folder",)
    expected: List = [["foo"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_list(as_block_value, common_values):
    block: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"),)
    expected: List = [[None, "a"], [2, "b"], [3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_list_with_initial_singleton(as_block_value, common_values):
    block: Tuple = ("i_text_in_folder", ("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"))
    expected: List = [["foo", None, "a"], ["foo", 2, "b"], ["foo", 3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_list_with_final_singleton(as_block_value, common_values):
    block: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"), "i_text_in_folder")
    expected: List = [[None, "a", "foo"], [2, "b", "foo"], [3, "c", "foo"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_list_with_no_columns(as_block_value, common_values):
    block: Tuple = (("i_list_in_folder",),)
    expected: List = [[], [], []]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_empty_list(as_block_value):
    block: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"),)
    expected: List = [[None, None]]
    actual: List = list(as_block_value(block, {}))
    assert actual == expected

def test_named_list(as_block_value, common_values):
    block: Tuple = (("i_named_list_in_root", "i_int_in_named_list", "i_text_in_named_list"),)
    expected: List = [["peter", None, "a"], ["paul", 2, "b"], ["mary", 3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_named_list_with_no_columns(as_block_value):
    block: Tuple = (("i_named_list_in_root",),)
    expected: List = [["peter"], ["paul"], ["mary"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_empty_named_list(as_block_value):
    block: Tuple = (("i_named_list_in_root", "i_int_in_named_list", "i_text_in_named_list"),)
    expected: List = [[None, None, None]]
    actual: List = list(as_block_value(block, {}))
    assert actual == expected

def test_nested_list(as_block_value, common_values):
    block: Tuple = ((
        "i_outer_nested_list",
        (
            "i_inner_nested_list",
            "i_text_in_inner_nested_list"
        ),
        "i_text_in_outer_nested_list"
    ),)
    expected: List = [
        [None, "a"],
        [None, "b"],
        ["foo", "c"],
        ["bar", "c"]
    ]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_nested_named_list(as_block_value, common_values):
    block: Tuple = ((
        "i_outer_nested_named_list",
        (
            "i_inner_nested_named_list",
            "i_text_in_inner_nested_named_list"
        ),
        "i_text_in_outer_nested_named_list"
    ),)
    expected: List = [
        ["peter", None, None, "a"],
        ["paul", None, None, "b"],
        ["mary", "orange", "foo", "c"],
        ["mary", "yellow", "bar", "c"]
    ]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

"""
def test_named_list_in_nested_list(as_block_value):
    pytest.fail()
"""

def test_empty_nested_named_list(as_block_value):
    value_set: ValueSet = ValueSet({}, {}, {})
    block: Tuple = (
        (
            "i_outer_nested_named_list",
            (
                "i_inner_nested_named_list",
                "i_text_in_inner_nested_named_list"
            ),
            "i_text_in_outer_nested_named_list"
        ),
    )
    expected: List = [[None, None, None, None]]
    actual: List = list(as_block_value(block, value_set))
    assert actual == expected

"""
def test_list_in_nested_named_list(as_block_value):
    pytest.fail()
"""
