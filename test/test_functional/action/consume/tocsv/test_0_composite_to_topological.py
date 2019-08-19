"""Polytropos composites are arbitrarily nested for organization, like a file system. Variable paths are subject to
change. However, the underlying variable IDs are constant and do not change, and they are only nested if there is a
one-to-many relationship.

The CSV converter works by first converting composites to a representation that reflects the underlying topology (by
variable ID), and then converting this representation to blocks of rows and columns (taking Cartesian products if
necessary).

This set of tests examines the system for converting select variables from the arbitrarily nested composite
representation to the fundamental topological representation..
"""
from typing import Tuple, Dict, Callable

import pytest
from polytropos.ontology.composite import Composite

from polytropos.actions.consume.tocsv.topo import Topological

@pytest.fixture()
def do_test(read_composite) -> Callable:
    def _do_test(block: Tuple, expected: Dict):
        composite: Composite = read_composite(2)
        topo: Topological = Topological(composite, "immutable")
        actual: Dict = topo(block)
        assert actual == expected
    return _do_test

def test_period_not_in_composite(read_composite):
    composite: Composite = read_composite(2)
    topo: Topological = Topological(composite, "201610")
    block: Tuple = ("i_text_in_folder",)
    expected: Dict = {}
    actual: Dict = topo(block)
    assert actual == expected

def test_singleton(do_test):
    block: Tuple = ("i_text_in_folder",)
    expected: Dict = {
        "i_text_in_folder": "foo"
    }
    do_test(block, expected)

def test_singleton_missing(do_test):
    block: Tuple = ("i_int_in_folder",)
    expected: Dict = {}
    do_test(block, expected)

def test_list(do_test):
    block: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder"),)
    expected: Dict = {
        "i_list_in_folder": [
            {},
            {"i_int_in_list_in_folder": 2},
            {"i_int_in_list_in_folder": 3}
        ],
    }
    do_test(block, expected)

def test_whole_list_missing(do_test):
    block: Tuple = (("i_list_in_root", "i_text_in_list"),)
    expected: Dict = {}
    do_test(block, expected)

def test_list_and_singleton(do_test):
    block: Tuple = ("i_text_in_folder", ("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"))
    expected: Dict = {
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
    }
    do_test(block, expected)

def test_list_with_no_columns(do_test):
    block: Tuple = (("i_list_in_folder",),)
    expected: Dict = {
        "i_list_in_folder": [{}, {}, {}]
    }
    do_test(block, expected)

def test_named_list(do_test):
    block: Tuple = (("i_named_list_in_root", "i_int_in_named_list", "i_text_in_named_list"),)
    expected: Dict = {
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
        }
    }
    do_test(block, expected)

def test_quadruply_nested(do_test):
    block: Tuple = (
        (
            "i_outer_nested_named_list",
            (
                "i_inner_nested_named_list",
                "i_text_in_inner_nested_named_list",
                (
                    "i_list_in_inner_nested_named_list",
                    "i_text_in_list_in_inner_nested_named_list",
                    (
                        "i_named_list_in_list_in_inner_nested_named_list",
                        "i_text_in_named_list_in_list_in_inner_nested_named_list"
                    )
                )
            ),
            "i_text_in_outer_nested_named_list"
        ),
    )
    # noinspection DuplicatedCode
    expected: Dict = {
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
                        "i_text_in_inner_nested_named_list": "bar",
                        "i_list_in_inner_nested_named_list": [
                            {"i_text_in_list_in_inner_nested_named_list": "black"},
                            {
                                "i_text_in_list_in_inner_nested_named_list": "white",
                                "i_named_list_in_list_in_inner_nested_named_list": {
                                    "this is extreme": {
                                        "i_text_in_named_list_in_list_in_inner_nested_named_list": "but it works"
                                    },
                                    "another one": {
                                        "i_text_in_named_list_in_list_in_inner_nested_named_list": "also ok"
                                    }
                                }
                            },
                        ]
                    }
                }
            }
        }
    }
    do_test(block, expected)
