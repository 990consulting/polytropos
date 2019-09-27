from collections import Callable
from typing import Dict, List

import pytest

from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track

@pytest.fixture()
def context() -> Context:
    return Context.build(conf_dir="dummy", data_dir="dummy")

@pytest.fixture()
def make_track() -> Callable:
    def _make_track(prefix: str) -> Track:
        spec: Dict = {
            "%s_Text" % prefix: {
                "data_type": "Text",
                "sort_order": 0,
                "name": "%s_Text" % prefix
            },
            "%s_Folder" % prefix: {
                "data_type": "Folder",
                "sort_order": 1,
                "name": "%s_Folder" % prefix
            },
            "%s_Folder_Text" % prefix: {
                "data_type": "Text",
                "sort_order": 0,
                "name": "%s_Folder_Text" % prefix,
                "parent": "%s_Folder" % prefix
            },
            "%s_List" % prefix: {
                "data_type": "List",
                "sort_order": 2,
                "name": "%s_List" % prefix
            },
            "%s_List_Text" % prefix: {
                "data_type": "Text",
                "sort_order": 0,
                "name": "%s_List_Text" % prefix,
                "parent": "%s_List" % prefix
            },
            "%s_KeyedList" % prefix: {
                "data_type": "KeyedList",
                "sort_order": 3,
                "name": "%s_KeyedList" % prefix
            },
            "%s_KeyedList_Text" % prefix: {
                "data_type": "Text",
                "sort_order": 0,
                "name": "%s_KeyedList_Text" % prefix,
                "parent": "%s_KeyedList" % prefix
            }
        }
        return Track(spec, None, prefix)

    return _make_track

@pytest.fixture()
def schema(make_track) -> Schema:
    immutable: Track = make_track("i")
    temporal: Track = make_track("t")
    return Schema(temporal, immutable)

@pytest.fixture()
def composite_1(schema) -> Composite:
    content: Dict = {
        "period_1": {
            "t_Text": "Not trivial",
            "t_Folder": {
                "t_Folder_Text": "Not trivial"
            },
            "t_List": [
                {"t_List_Text": "Not trivial"}
            ],
            "t_KeyedList": {
                "a key": {"t_KeyedList_Text": "Not trivial"}
            }
        },
        "period_2": {
            "t_Text": None,
            "t_Folder": {},
            "t_List": [],
            "t_KeyedList": {}
        },
        "immutable": {}
    }
    return Composite(schema, content, composite_id="composite_1")

@pytest.fixture()
def composite_2(schema) -> Composite:
    content: Dict = {
        "period_1": {},
        "immutable": {
            "i_Text": "",
        }
    }
    return Composite(schema, content, composite_id="composite_2")

@pytest.fixture()
def composite_3(schema) -> Composite:
    content: Dict = {
        "immutable": {
            "i_Text": "Not trivial",
            "i_Folder": {
                "i_Folder_Text": "Not trivial"
            },
            "i_List": [
                {"i_List_Text": "Not trivial"}
            ],
            "i_KeyedList": {
                "a key": {"i_KeyedList_Text": "Not trivial"}
            }
        }
    }
    return Composite(schema, content, composite_id="composite_3")

@pytest.fixture()
def composites(composite_1, composite_2, composite_3) -> List[Composite]:
    return [composite_1, composite_2, composite_3]
