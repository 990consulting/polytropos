from typing import Dict

import pytest

from polytropos.ontology.track import Track

@pytest.fixture
def empty_track() -> Track:
    return Track.build({}, None, "empty")

@pytest.fixture
def simple_track() -> Track:
    specs: Dict = {
        "text_in_root": {
            "name": "some_text",
            "data_type": "Text",
            "sort_order": 0
        },
        "folder_in_root": {
            "name": "outer",
            "data_type": "Folder",
            "sort_order": 1
        },
        "text_in_folder": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_root",
            "sort_order": 0
        },
        "folder_in_folder": {
            "name": "inner",
            "data_type": "Folder",
            "parent": "folder_in_root",
            "sort_order": 1
        },
        "text_in_folder_in_folder": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_folder",
            "sort_order": 0
        }
    }
    return Track.build(specs, None, "simple")

@pytest.fixture
def complex_track() -> Track:
    specs: Dict = {
        "list_in_root": {
            "name": "outer",
            "data_type": "List",
            "sort_order": 0
        },
        "folder_in_list": {
            "name": "the_folder",
            "data_type": "Folder",
            "parent": "list_in_root",
            "sort_order": 0
        },
        "list_in_folder_in_list": {
            "name": "inner",
            "data_type": "List",
            "parent": "folder_in_list",
            "sort_order": 0
        },
        "text_in_list_in_folder_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "list_in_folder_in_list",
            "sort_order": 0
        }
    }
    return Track.build(specs, None, "simple")

@pytest.fixture
def period() -> str:
    return "201410"

@pytest.fixture
def entity_id() -> str:
    return "012345678"

