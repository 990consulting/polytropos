import pytest

from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
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
                        "i_text_in_inner_nested_list": "bar",
                        "i_keyed_list_in_inner_nested_list": {
                            "black": {"i_text_in_keyed_list_in_inner_nested_list": "white"},
                            "green": {"i_text_in_keyed_list_in_inner_nested_list": "red"}
                        }
                    }
                ]
            }
        ],
        "i_keyed_list_in_root": {
            "peter": {
                "i_text_in_keyed_list": "a"
            },
            "paul": {
                "i_text_in_keyed_list": "b",
                "i_int_in_keyed_list": 2
            },
            "mary": {
                "i_text_in_keyed_list": "c",
                "i_int_in_keyed_list": 3
            }
        },
        "i_outer_nested_keyed_list": {
            "peter": {
                "i_text_in_outer_nested_keyed_list": "a"
            },
            "paul": {
                "i_text_in_outer_nested_keyed_list": "b",
                "i_inner_nested_keyed_list": {
                    "red": {}
                }
            },
            "mary": {
                "i_text_in_outer_nested_keyed_list": "c",
                "i_inner_nested_keyed_list": {
                    "orange": {
                        "i_text_in_inner_nested_keyed_list": "foo"
                    },
                    "yellow": {
                        "i_text_in_inner_nested_keyed_list": "bar",
                        "i_list_in_inner_nested_keyed_list": [
                            {"i_text_in_list_in_inner_nested_keyed_list": "black"},
                            {
                                "i_text_in_list_in_inner_nested_keyed_list": "white",
                                "i_keyed_list_in_list_in_inner_nested_keyed_list": {
                                    "this is extreme": {
                                        "i_text_in_keyed_list_in_list_in_inner_nested_keyed_list": "but it works"
                                    },
                                    "another one": {
                                        "i_text_in_keyed_list_in_list_in_inner_nested_keyed_list": "also ok"
                                    }
                                }
                            },
                        ]
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

def test_keyed_list(as_block_value, common_values):
    block: Tuple = (("i_keyed_list_in_root", "i_int_in_keyed_list", "i_text_in_keyed_list"),)
    expected: List = [["peter", None, "a"], ["paul", 2, "b"], ["mary", 3, "c"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_keyed_list_with_no_columns(as_block_value, common_values):
    block: Tuple = (("i_keyed_list_in_root",),)
    expected: List = [["peter"], ["paul"], ["mary"]]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_empty_keyed_list(as_block_value):
    block: Tuple = (("i_keyed_list_in_root", "i_int_in_keyed_list", "i_text_in_keyed_list"),)
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

def test_nested_keyed_list(as_block_value, common_values):
    block: Tuple = ((
        "i_outer_nested_keyed_list",
        (
            "i_inner_nested_keyed_list",
            "i_text_in_inner_nested_keyed_list"
        ),
        "i_text_in_outer_nested_keyed_list"
    ),)
    expected: List = [
        ["peter", None, None, "a"],
        ["paul", "red", None, "b"],
        ["mary", "orange", "foo", "c"],
        ["mary", "yellow", "bar", "c"]
    ]
    actual: List = list(as_block_value(block, common_values))
    assert actual == expected

def test_empty_nested_keyed_list(as_block_value):
    values: Dict = {}
    block: Tuple = (
        (
            "i_outer_nested_keyed_list",
            (
                "i_inner_nested_keyed_list",
                "i_text_in_inner_nested_keyed_list"
            ),
            "i_text_in_outer_nested_keyed_list"
        ),
    )
    expected: List = [[None, None, None, None]]
    actual: List = list(as_block_value(block, values))
    assert actual == expected

def test_list_in_nested_keyed_list(as_block_value, common_values):
    block: Tuple = (
        (
            "i_outer_nested_keyed_list",
            (
                "i_inner_nested_keyed_list",
                "i_text_in_inner_nested_keyed_list",
                (
                    "i_list_in_inner_nested_keyed_list",
                    "i_text_in_list_in_inner_nested_keyed_list"
                )
            ),
            "i_text_in_outer_nested_keyed_list"
        ),
    )
    expected: List = [
        ["peter", None, None, None, "a"],
        ["paul", "red", None, None, "b"],
        ["mary", "orange", "foo", None, "c"],
        ["mary", "yellow", "bar", "black", "c"],
        ["mary", "yellow", "bar", "white", "c"],
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_keyed_list_in_nested_list(as_block_value, common_values):
    block: Tuple = (
        (
            "i_outer_nested_list",
            (
                "i_inner_nested_list",
                "i_text_in_inner_nested_list",
                (
                    "i_keyed_list_in_inner_nested_list",
                    "i_text_in_keyed_list_in_inner_nested_list"
                )
            ),
            "i_text_in_outer_nested_list"
        ),
    )
    expected: List = [
        [None, None, None, "a"],
        [None, None, None, "b"],
        ["foo", None, None, "c"],
        ["bar", "black", "white", "c"],
        ["bar", "green", "red", "c"],
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual

def test_quadruple_nesting(common_values, as_block_value):
    block: Tuple = (
        (
            "i_outer_nested_keyed_list",
            (
                "i_inner_nested_keyed_list",
                "i_text_in_inner_nested_keyed_list",
                (
                    "i_list_in_inner_nested_keyed_list",
                    "i_text_in_list_in_inner_nested_keyed_list",
                    (
                        "i_keyed_list_in_list_in_inner_nested_keyed_list",
                        "i_text_in_keyed_list_in_list_in_inner_nested_keyed_list"
                    )
                )
            ),
            "i_text_in_outer_nested_keyed_list"
        ),
    )
    expected: List = [
        ["peter", None, None, None, None, None, "a"],
        ["paul", "red", None, None, None, None, "b"],
        ["mary", "orange", "foo", None, None, None, "c"],
        ["mary", "yellow", "bar", "black", None, None, "c"],
        ["mary", "yellow", "bar", "white", "this is extreme", "but it works", "c"],
        ["mary", "yellow", "bar", "white", "another one", "also ok", "c"],
    ]
    actual: List = list(as_block_value(block, common_values))
    assert expected == actual
