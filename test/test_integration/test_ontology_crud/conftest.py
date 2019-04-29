from typing import Dict

import pytest

from etl4.ontology.track import Track
from etl4.ontology.variable import Variable

@pytest.fixture()
def source_nested_dict_track() -> Track:
    spec: Dict = {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder_1",
            "sort_order": 0
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder_2",
            "sort_order": 0
        },
        "source_folder_1": {
            "name": "outer_s",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_folder_2": {
            "name": "inner_s",
            "data_type": "Folder",
            "parent": "source_folder_1",
            "sort_order": 1
        },
        "source_var_3": {
            "name": "third_source",
            "data_type": "Integer",
            "parent": "source_folder_2",
            "sort_order": 1
        },
        "source_folder_3": {
            "name": "initially_empty_folder",
            "data_type": "Folder",
            "sort_order": 1
        }
    }
    return Track.build(spec, None, "Source")

@pytest.fixture()
def target_nested_dict_track(source_nested_dict_track) -> Track:
    spec: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "parent": "target_folder_1",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "sources": ["source_var_2"],
            "parent": "target_folder_2",
            "sort_order": 0
        },
        "target_folder_1": {
            "name": "outer_s",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_folder_2": {
            "name": "inner_s",
            "data_type": "Folder",
            "parent": "target_folder_1",
            "sort_order": 1
        }
    }
    return Track(spec, source_nested_dict_track, "Target")
