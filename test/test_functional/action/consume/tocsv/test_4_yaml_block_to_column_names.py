"""Tests to create the same blocks as are used in test_1_as_block_values."""
from typing import Tuple, List, Callable, Type, Iterator

import pytest
import yaml

from polytropos.actions.consume.tocsv.descriptors.colnames import DescriptorBlockToColumnNames

@pytest.fixture()
def to_column_names(schema) -> Callable:   # Schema defined in conftest.py, in this directory
    def _to_column_names(raw_yaml: str) -> Iterator:
        descriptors: List = yaml.full_load(raw_yaml)
        y2c: DescriptorBlockToColumnNames = DescriptorBlockToColumnNames(schema)
        return y2c(descriptors)
    return _to_column_names

@pytest.fixture()
def do_test(to_column_names) -> Callable:
    def _ret(raw_yaml: str, expected: Tuple):
        actual: Tuple = tuple(to_column_names(raw_yaml))
        assert actual == expected
    return _ret

def test_singleton(do_test):
    raw_yaml: str = """
    - i_text_in_folder
    """
    expected: Tuple = ("/i_folder/some_text",)  # See note in descriptors.py for how to obtain this
    do_test(raw_yaml, expected)

def test_singleton_custom_name(do_test):
    """If a list item is a dictionary with a single key-value pair, then the key is the actual data to be put in the
    column and the value is the name of the column. This should not matter for block creation."""
    raw_yaml: str = """
    - i_text_in_folder: my_special_name
    """
    expected: Tuple = ("my_special_name",)
    do_test(raw_yaml, expected)

def test_list(do_test):
    raw_yaml: str = """
    - i_list_in_folder:
        type: List
        children:
          - i_int_in_list_in_folder
          - i_text_in_list_in_folder
    """
    expected: Tuple = ("/i_folder/simple_list/some_int", "/i_folder/simple_list/some_text")
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
    expected: Tuple = ("special_name_1", "special_name_2")
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
    expected: Tuple = ("/i_folder/some_text", "/i_folder/simple_list/some_int", "/i_folder/simple_list/some_text")
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
    expected: Tuple = ("/i_folder/simple_list/some_int", "/i_folder/simple_list/some_text", "special_name")
    do_test(raw_yaml, expected)

def test_list_with_no_columns(do_test):
    raw_yaml: str = """
    - i_list_in_folder:
        type: List
    """
    expected: Tuple = ()
    do_test(raw_yaml, expected)

def test_named_list(do_test):
    raw_yaml: str = """
    - i_named_list_in_root:
        type: NamedList
        children:
          - i_int_in_named_list
          - i_text_in_named_list
    """
    expected: Tuple = ("/simple_named_list", "/simple_named_list/some_int", "/simple_named_list/some_text")
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
    expected: Tuple = ("special_name_for_key_column", "name_1", "name_2")
    do_test(raw_yaml, expected)

def test_named_list_with_no_columns(do_test):
    raw_yaml: str = """
    - i_named_list_in_root:
        type: NamedList
    """
    expected: Tuple = ("/simple_named_list",)
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
    expected: Tuple = ("/outer_list/inner_list/some_text", "/outer_list/some_text")
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
    expected: Tuple = (
        "/outer_named_list",
        "/outer_named_list/inner_named_list",
        "/outer_named_list/inner_named_list/some_text",
        "/outer_named_list/some_text"
    )
    do_test(raw_yaml, expected)

def test_list_in_nested_named_list(do_test):
    raw_yaml: str = """
    - i_outer_nested_named_list:
        type: NamedList
        children:
            - i_inner_nested_named_list:
                type: NamedList
                key_column_name: "THIS AFFECTS ONLY THIS COLUMN"
                children:
                    - i_text_in_inner_nested_named_list
                    - i_list_in_inner_nested_named_list:
                        type: List
                        children:
                            - i_text_in_list_in_inner_nested_named_list
            - i_text_in_outer_nested_named_list
    """
    expected: Tuple = (
        "/outer_named_list",
        "THIS AFFECTS ONLY THIS COLUMN",
        "/outer_named_list/inner_named_list/some_text",
        "/outer_named_list/inner_named_list/a_list/some_text",
        "/outer_named_list/some_text"
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
                            - i_text_in_named_list_in_inner_nested_list
            - i_text_in_outer_nested_list
    """
    expected: Tuple = (
        "/outer_list/inner_list/some_text",
        "/outer_list/inner_list/a_named_list",
        "/outer_list/inner_list/a_named_list/some_text",
        "/outer_list/some_text"
    )
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
        "/outer_named_list",
        "/outer_named_list/inner_named_list",
        "/outer_named_list/inner_named_list/some_text",
        "/outer_named_list/inner_named_list/a_list/some_text",
        "/outer_named_list/inner_named_list/a_list/yet_another_named_list",
        "/outer_named_list/inner_named_list/a_list/yet_another_named_list/some_text",
        "/outer_named_list/some_text"
    )
    do_test(raw_yaml, expected)
