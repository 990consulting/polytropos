from typing import Dict

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track

@pytest.fixture()
def temporal_track() -> Track:
    specs: Dict = {
        "t_folder_in_root": {
            "name": "t_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "t_text_in_folder": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "t_folder_in_root",
            "sort_order": 0
        },
        "t_text_in_root": {
            "name": "some_text",
            "data_type": "Text",
            "sort_order": 1
        },
        "t_list_in_root": {
            "name": "t_list",
            "data_type": "List",
            "sort_order": 2
        },
        "t_text_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "t_list_in_root",
            "sort_order": 0
        }
    }
    return Track.build(specs, None, "temporal")

@pytest.fixture()
def immutable_track() -> Track:
    specs: Dict = {
        "i_folder_in_root": {
            "name": "i_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "i_text_in_folder": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_folder_in_root",
            "sort_order": 0
        },
        "i_list_in_folder": {
            "name": "simple_list",
            "data_type": "List",
            "parent": "i_folder_in_root",
            "sort_order": 1
        },
        "i_text_in_list_in_folder": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_list_in_folder",
            "sort_order": 0
        },
        "i_int_in_list_in_folder": {
            "name": "some_int",
            "data_type": "Integer",
            "parent": "i_list_in_folder",
            "sort_order": 0
        },
        "i_list_in_root": {
            "name": "simple_list",
            "data_type": "List",
            "sort_order": 1
        },
        "i_text_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_list_in_root",
            "sort_order": 0
        },
        "i_outer_nested_list": {
            "name": "outer_list",
            "data_type": "List",
            "sort_order": 2
        },
        "i_text_in_outer_nested_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_outer_nested_list",
            "sort_order": 0
        },
        "i_inner_nested_list": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "i_outer_nested_list",
            "sort_order": 1
        },
        "i_text_in_inner_nested_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_inner_nested_list",
            "sort_order": 0
        },
        "i_named_list_in_inner_nested_list": {
            "name": "a_named_list",
            "data_type": "List",
            "parent": "i_inner_nested_list",
            "sort_order": 1
        },
        "i_text_in_named_list_in_inner_nested_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_named_list_in_inner_nested_list",
            "sort_order": 0
        },
        "i_named_list_in_root": {
            "name": "simple_named_list",
            "data_type": "NamedList",
            "sort_order": 3
        },
        "i_text_in_named_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_named_list_in_root",
            "sort_order": 0
        },
        "i_int_in_named_list": {
            "name": "some_int",
            "data_type": "Integer",
            "parent": "i_named_list_in_root",
            "sort_order": 1
        },
        "i_outer_nested_named_list": {
            "name": "outer_named_list",
            "data_type": "NamedList",
            "sort_order": 4
        },
        "i_text_in_outer_nested_named_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_outer_nested_named_list",
            "sort_order": 0
        },
        "i_inner_nested_named_list": {
            "name": "inner_named_list",
            "data_type": "NamedList",
            "parent": "i_outer_nested_named_list",
            "sort_order": 1
        },
        "i_text_in_inner_nested_named_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_inner_nested_named_list",
            "sort_order": 0
        },
        "i_list_in_inner_nested_named_list": {
            "name": "a_list",
            "data_type": "List",
            "parent": "i_inner_nested_named_list",
            "sort_order": 1
        },
        "i_text_in_list_in_inner_nested_named_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "i_list_in_inner_nested_named_list",
            "sort_order": 0
        },
    }
    return Track.build(specs, None, "immutable")

@pytest.fixture()
def schema(temporal_track, immutable_track) -> Schema:
    return Schema(temporal_track, immutable_track)

@pytest.fixture()
def composite_1(schema) -> Composite:
    # Read from file -- this one should have everything and lots of periods
    pass

@pytest.fixture()
def composite_2(schema) -> Composite:
    # Read from file -- this one should have only immutable
    pass

@pytest.fixture()
def composite_3(schema) -> Composite:
    # Read from file -- this one should have only temporal
    pass
