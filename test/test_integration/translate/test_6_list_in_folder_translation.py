import pytest
from typing import Dict, Tuple

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
            "source_inner_named_list": {
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
        "source_named_list": {
            "name": "source_inner_named_list",
            "data_type": "NamedList",
            "parent": "source_folder",
            "sort_order": 1
        },
        "source_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_named_list",
            "sort_order": 0
        }
    }
    return spec, doc

def target_flattened() -> Tuple[Dict, Dict]:
    doc: Dict = {
        "the_list": [
            {
                "name": "Steve",
                "color": "red"
            },
            {
                "name": "Samantha",
                "color": "blue"
            }
        ],
        "the_named_list": {
            "Anne": {
                "color": "orange"
            },
            "Janet": {
                "color": "green"
            }
        }
    }

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
        "target_named_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "sort_order": 1,
            "sources": ["source_named_list"],
        },
        "target_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_named_list",
            "sort_order": 0,
            "sources": ["source_named_list_color"]
        }
    }

    return spec, doc

def target_nested() -> Tuple[Dict, Dict]:
    doc: Dict = {
        "outer": {
            "inner": {
                "the_named_list": {
                    "Anne": {
                        "color": "orange"
                    },
                    "Janet": {
                        "color": "green"
                    }
                }
            },
            "the_list": [
                {
                    "name": "Steve",
                    "color": "red"
                },
                {
                    "name": "Samantha",
                    "color": "blue"
                }
            ]
        }
    }

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
        "target_named_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "parent": "target_folder_inner",
            "sort_order": 0,
            "sources": ["source_named_list"],
        },
        "target_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_named_list",
            "sort_order": 0,
            "sources": ["source_named_list_color"]
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
    actual: Dict = translate(source_doc)
    assert actual == expected
