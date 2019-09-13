from collections import OrderedDict
import pytest
from typing import Dict, Tuple, Any

from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator

@pytest.fixture()
def source() -> Tuple[Dict, Dict]:
    doc: Dict = {
        "source_outer_folder": {
            "source_inner_list": [
                {
                    "name": "Steve",
                    "color": "red"
                },
                {
                    "name": "Samantha",
                    "color": "blue"
                }
            ],
            "source_inner_keyed_list": {
                "Anne": {
                    "color": "orange"
                },
                "Janet": {
                    "color": "green"
                }
            }
        }
    }

    spec: Dict = {
        "source_folder": {
            "name": "source_outer_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_list": {
            "name": "source_inner_list",
            "data_type": "List",
            "parent": "source_folder",
            "sort_order": 0,
        },
        "source_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 0
        },
        "source_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 1
        },
        "source_keyed_list": {
            "name": "source_inner_keyed_list",
            "data_type": "KeyedList",
            "parent": "source_folder",
            "sort_order": 1
        },
        "source_keyed_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_keyed_list",
            "sort_order": 0
        }
    }
    return spec, doc

def target_flattened() -> Tuple[Dict, "OrderedDict[str, Any]"]:
    doc: OrderedDict[str, Any] = OrderedDict([
        ("the_list", [
            OrderedDict([
                ("name", "Steve"),
                ("color", "red")
            ]),
            OrderedDict([
                ("name", "Samantha"),
                ("color", "blue")
            ])
        ]),
        ("the_keyed_list", OrderedDict([
            ("Anne", OrderedDict([
                ("color", "orange")
            ])),
            ("Janet", OrderedDict([
                ("color", "green")
            ]))
        ]))
    ])

    spec: Dict = {
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["source_list"],
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0,
            "sources": ["source_list_name"]
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 1,
            "sources": ["source_list_color"]
        },
        "target_keyed_list": {
            "name": "the_keyed_list",
            "data_type": "KeyedList",
            "sort_order": 1,
            "sources": ["source_keyed_list"],
        },
        "target_keyed_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_keyed_list",
            "sort_order": 0,
            "sources": ["source_keyed_list_color"]
        }
    }

    return spec, doc

def target_nested() -> Tuple[Dict, "OrderedDict[str, Any]"]:
    doc: OrderedDict[str, Any] = OrderedDict([
        ("outer", OrderedDict([
            ("inner", OrderedDict([
                ("the_keyed_list", OrderedDict([
                    ("Anne", OrderedDict([
                        ("color", "orange")
                    ])),
                    ("Janet", OrderedDict([
                        ("color", "green")
                    ]))
                ]))
            ])),
            ("the_list", [
                OrderedDict([
                    ("name", "Steve"),
                    ("color", "red")
                ]),
                OrderedDict([
                    ("name", "Samantha"),
                    ("color", "blue")
                ])
            ])
        ]))
    ])

    spec: Dict = {
        "target_folder_outer": {
            "name": "outer",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_folder_inner": {
            "name": "inner",
            "data_type": "Folder",
            "parent": "target_folder_outer",
            "sort_order": 0
        },
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "parent": "target_folder_outer",
            "sort_order": 1,
            "sources": ["source_list"],
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0,
            "sources": ["source_list_name"]
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 1,
            "sources": ["source_list_color"]
        },
        "target_keyed_list": {
            "name": "the_keyed_list",
            "data_type": "KeyedList",
            "parent": "target_folder_inner",
            "sort_order": 0,
            "sources": ["source_keyed_list"],
        },
        "target_keyed_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_keyed_list",
            "sort_order": 0,
            "sources": ["source_keyed_list_color"]
        }
    }

    return spec, doc

@pytest.mark.parametrize("target", [target_nested, target_flattened])
def test_list_in_folder(source, target):
    source_spec, source_doc = source
    target_spec, expected = target()
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected
