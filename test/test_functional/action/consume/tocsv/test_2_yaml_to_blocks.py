"""Tests to create the same blocks as are used in test_1_as_block_values."""
from typing import Tuple, List, Callable, Type

import pytest
import yaml

from polytropos.actions.consume.tocsv.descriptors import DescriptorsToBlocks

@pytest.fixture()
def to_blocks() -> Callable:
    def _to_blocks(raw_yaml: str) -> Tuple:
        descriptors: List = yaml.full_load(raw_yaml)
        y2b: DescriptorsToBlocks = DescriptorsToBlocks()
        return y2b(descriptors)
    return _to_blocks

@pytest.fixture()
def do_test(to_blocks) -> Callable:
    def _ret(raw_yaml: str, expected: Tuple):
        actual: Tuple = to_blocks(raw_yaml)
        assert actual == expected
    return _ret

def test_singleton(do_test):
    raw_yaml: str = """
    - i_text_in_folder
    """
    expected: Tuple = ("i_text_in_folder",)
    do_test(raw_yaml, expected)

def test_singleton_custom_name(do_test):
    """If a list item is a dictionary with a single key-value pair, then the key is the actual data to be put in the
    column and the value is the name of the column. This should not matter for block creation."""
    raw_yaml: str = """
    - i_text_in_folder: my_special_name
    """
    expected: Tuple = ("i_text_in_folder",)
    do_test(raw_yaml, expected)

def test_list(do_test):
    raw_yaml: str = """
    - i_list_in_folder:
        type: List
        children:
          - i_int_in_list_in_folder
          - i_text_in_list_in_folder
    """
    expected: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"),)
    do_test(raw_yaml, expected)

def test_list_custom_names(do_test):
    """The rule for custom column names also applies to elements of lists. The list root isn't associated with any
    columns, so there's no way to specify a column name for that."""
    raw_yaml: str = """
    - i_list_in_folder:
        type: List
        children:
          - i_int_in_list_in_folder: special_name_1
          - i_text_in_list_in_folder: special_name_2
    """
    expected: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"),)
    do_test(raw_yaml, expected)

def test_list_with_initial_singleton(do_test):
    raw_yaml: str = """
    - i_text_in_folder
    - i_list_in_folder:
        type: List
        children:
          - i_int_in_list_in_folder
          - i_text_in_list_in_folder
    """
    expected: Tuple = ("i_text_in_folder", ("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"))
    do_test(raw_yaml, expected)

def test_list_with_final_singleton(do_test):
    raw_yaml: str = """
    - i_list_in_folder:
        type: List
        children:
          - i_int_in_list_in_folder
          - i_text_in_list_in_folder
    - i_text_in_folder: special_name
    """
    expected: Tuple = (("i_list_in_folder", "i_int_in_list_in_folder", "i_text_in_list_in_folder"), "i_text_in_folder")
    do_test(raw_yaml, expected)

def test_list_with_no_columns(do_test):
    raw_yaml: str = """
    - i_list_in_folder:
        type: List
    """
    expected: Tuple = (("i_list_in_folder",),)
    do_test(raw_yaml, expected)

def test_named_list(do_test):
    raw_yaml: str = """
    - i_named_list_in_root:
        type: NamedList
        children:
          - i_int_in_named_list
          - i_text_in_named_list
    """
    expected: Tuple = (("i_named_list_in_root", "i_int_in_named_list", "i_text_in_named_list"),)
    do_test(raw_yaml, expected)

def test_named_list_custom_column_names(do_test):
    """Named lists have an extra column for the name of the list item. By default, the column name is the named list
    root, but custom column names must be possible here as well, so a special key is supplied. Again, this should not
    affect the composition of the column data block."""
    raw_yaml: str = """
    - i_named_list_in_root:
        type: NamedList
        key_column_name: special_name_for_key_column
        children:
          - i_int_in_named_list: name_1
          - i_text_in_named_list: name_2
    """
    expected: Tuple = (("i_named_list_in_root", "i_int_in_named_list", "i_text_in_named_list"),)
    do_test(raw_yaml, expected)

def test_named_list_with_no_columns(do_test):
    raw_yaml: str = """
    - i_named_list_in_root:
        type: NamedList
    """
    expected: Tuple = (("i_named_list_in_root",),)
    do_test(raw_yaml, expected)

def test_nested_list(do_test):
    raw_yaml: str = """
    - i_outer_nested_list:
        type: List
        children:
            - i_inner_nested_list:
                type: List
                children:
                    - i_text_in_inner_nested_list
            - i_text_in_outer_nested_list
    """
    expected: Tuple = ((
        "i_outer_nested_list",
        (
            "i_inner_nested_list",
            "i_text_in_inner_nested_list"
        ),
        "i_text_in_outer_nested_list"
    ),)
    do_test(raw_yaml, expected)

def test_nested_named_list(do_test):
    raw_yaml: str = """
    - i_outer_nested_named_list:
        type: NamedList
        children:
            - i_inner_nested_named_list:
                type: NamedList
                children:
                    - i_text_in_inner_nested_named_list
            - i_text_in_outer_nested_named_list
    """
    expected: Tuple = ((
        "i_outer_nested_named_list",
        (
            "i_inner_nested_named_list",
            "i_text_in_inner_nested_named_list"
        ),
        "i_text_in_outer_nested_named_list"
    ),)
    do_test(raw_yaml, expected)

def test_list_in_nested_named_list(do_test):
    raw_yaml: str = """
    - i_outer_nested_named_list:
        type: NamedList
        children:
            - i_inner_nested_named_list:
                type: NamedList
                children:
                    - i_text_in_inner_nested_named_list
                    - i_list_in_inner_nested_named_list:
                        type: List
                        children:
                            - i_text_in_list_in_inner_nested_named_list
            - i_text_in_outer_nested_named_list
    """
    expected: Tuple = (
        (
            "i_outer_nested_named_list",
            (
                "i_inner_nested_named_list",
                "i_text_in_inner_nested_named_list",
                (
                    "i_list_in_inner_nested_named_list",
                    "i_text_in_list_in_inner_nested_named_list"
                )
            ),
            "i_text_in_outer_nested_named_list"
        ),
    )
    do_test(raw_yaml, expected)

def test_named_list_in_nested_list(do_test):
    raw_yaml: str = """
    - i_outer_nested_list:
        type: List
        children:
            - i_inner_nested_list:
                type: List
                children:
                    - i_text_in_inner_nested_list
                    - i_named_list_in_inner_nested_list:
                        type: NamedList
                        children:
                            - i_text_in_named_list_in_inner_nested_list: special_name
            - i_text_in_outer_nested_list
    """
    expected: Tuple = ((
        "i_outer_nested_list",
        (
            "i_inner_nested_list",
            "i_text_in_inner_nested_list",
            (
                "i_named_list_in_inner_nested_list",
                "i_text_in_named_list_in_inner_nested_list"
            )
        ),
        "i_text_in_outer_nested_list"
    ),)
    do_test(raw_yaml, expected)

def test_quadruple_nesting(do_test):
    raw_yaml: str = """
    - i_outer_nested_named_list:
        type: NamedList
        children:
            - i_inner_nested_named_list:
                type: NamedList
                children:
                    - i_text_in_inner_nested_named_list
                    - i_list_in_inner_nested_named_list:
                        type: List
                        children:
                            - i_text_in_list_in_inner_nested_named_list
                            - i_named_list_in_list_in_inner_nested_named_list:
                                type: NamedList
                                children:
                                    - i_text_in_named_list_in_list_in_inner_nested_named_list
            - i_text_in_outer_nested_named_list
    """
    expected: Tuple = (
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
    do_test(raw_yaml, expected)
