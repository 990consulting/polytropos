import pytest
from typing import Dict, Tuple
from polytropos.ontology.track import Track
from polytropos.transform.translate import Translate

@pytest.fixture
def source() -> Tuple[Dict, Dict]:
    source_doc: Dict = {
        "outer_list_1": [
            {
                "inner_list": [
                    {"name": "inner_1_1_1"},
                    {"name": "inner_1_1_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_1_2_1"},
                    {"name": "inner_1_2_2"}
                ]
            }
        ],
        "outer_list_2": [
            {
                "inner_list": [
                    {"name": "inner_2_1_1"},
                    {"name": "inner_2_1_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_2_2_1"},
                    {"name": "inner_2_2_2"}
                ]
            }
        ]
    }
    source_spec: Dict = {
        "outer_list_1_id": {
            "name": "outer_list_1",
            "data_type": "List",
            "sort_order": 0
        },
        "inner_list_1_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_1_id",
            "sort_order": 0
        },
        "name_1_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_1_id",
            "sort_order": 0
        },
        "outer_list_2_id": {
            "name": "outer_list_2",
            "data_type": "List",
            "sort_order": 1
        },
        "inner_list_2_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_2_id",
            "sort_order": 0
        },
        "name_2_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_2_id",
            "sort_order": 0
        }
    }

    return source_spec, source_doc

@pytest.fixture
def target() -> Tuple[Dict, Dict]:
    target_doc: Dict = {
        "outer_list": [
            {
                "inner_list": [
                    {"name": "inner_1_1_1"},
                    {"name": "inner_1_1_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_1_2_1"},
                    {"name": "inner_1_2_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_2_1_1"},
                    {"name": "inner_2_1_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_2_2_1"},
                    {"name": "inner_2_2_2"}
                ]
            }
        ]
    }

    target_spec: Dict = {
        "outer_list_id": {
            "name": "outer_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["outer_list_1_id", "outer_list_2_id"]
        },
        "inner_list_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_id",
            "sort_order": 0,
            "sources": ["inner_list_1_id", "inner_list_2_id"]
        },
        "name_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_id",
            "sort_order": 0,
            "sources": ["name_1_id", "name_2_id"]
        }
    }

    return target_spec, target_doc

def test_nested_list(source, target):
    """Reversing the order of the sources in the target list spec results in an equivalent change in the order of the
    resulting list."""
    source_spec, source_doc = source
    target_spec, target_doc = target
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translate = Translate(target_track)
    actual: Dict = translate(source_doc)
    assert actual == target_doc
