import random
from collections import OrderedDict
import pytest
from typing import Dict, Tuple, List, Any

from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator
import itertools

def source_nested() -> Tuple[Dict, Dict]:
    source_doc: Dict = {
        "the_list": [
            {
                "day": "Tuesday",
                "the_folder": {
                    "name": "Steve",
                    "color": "orange"
                }
            },
            {
                "day": "Monday",
                "the_folder": {
                    "name": "Susan",
                    "color": "mauve"
                }
            }
        ],
        "meaning_of_life": 42
    }

    source_spec: Dict = {
        "source_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0
        },
        "source_list_day": {
            "name": "day",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 0
        },
        "source_list_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "parent": "source_list",
            "sort_order": 1
        },
        "source_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_list_folder",
            "sort_order": 0
        },
        "source_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_list_folder",
            "sort_order": 1
        },
        "source_meaning_of_life": {
            "name": "meaning_of_life",
            "data_type": "Integer",
            "sort_order": 1
        }
    }
    return source_spec, source_doc

def source_flat() -> Tuple[Dict, Dict]:
    source_doc: Dict = {
        "the_list": [
            {
                "day": "Tuesday",
                "name": "Steve",
                "color": "orange"
            },
            {
                "day": "Monday",
                "name": "Susan",
                "color": "mauve"
            }
        ],
        "meaning_of_life": 42
    }

    source_spec: Dict = {
        "source_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0
        },
        "source_list_day": {
            "name": "day",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 0
        },
        "source_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 1
        },
        "source_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 2
        },
        "source_meaning_of_life": {
            "name": "meaning_of_life",
            "data_type": "Integer",
            "sort_order": 1
        }
    }
    return source_spec, source_doc

def target_nested() -> Tuple[Dict, "OrderedDict[str, Any]"]:
    target_doc: OrderedDict[str, Any] = OrderedDict([
        ("the_list", [
            OrderedDict([
                ("day", "Tuesday"),
                ("the_folder", OrderedDict([
                    ("name", "Steve"),
                    ("color", "orange")
                ]))
            ]),
            OrderedDict([
                ("day", "Monday"),
                ("the_folder", OrderedDict([
                    ("name", "Susan"),
                    ("color", "mauve")
                ]))
            ])
        ]),
        ("meaning_of_life", 42)
    ])

    target_spec: Dict = {
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["source_list"],
        },
        "target_list_day": {
            "name": "day",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0,
            "sources": ["source_list_day"]
        },
        "target_list_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "parent": "target_list",
            "sort_order": 1
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list_folder",
            "sort_order": 0,
            "sources": ["source_list_name"],
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list_folder",
            "sort_order": 1,
            "sources": ["source_list_color"]
        },
        "target_meaning_of_life": {
            "name": "meaning_of_life",
            "data_type": "Integer",
            "sort_order": 1,
            "sources": ["source_meaning_of_life"]
        }
    }
    return target_spec, target_doc

def target_flat() -> Tuple[Dict, "OrderedDict[str, Any]"]:
    target_doc: OrderedDict[str, Any] = OrderedDict([
        ("the_list", [
            OrderedDict([
                ("day", "Tuesday"),
                ("name", "Steve"),
                ("color", "orange")
            ]),
            OrderedDict([
                ("day", "Monday"),
                ("name", "Susan"),
                ("color", "mauve")
            ])
        ]),
        ("meaning_of_life", 42)
    ])

    target_spec: Dict = {
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["source_list"],
        },
        "target_list_day": {
            "name": "day",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0,
            "sources": ["source_list_day"]
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 1,
            "sources": ["source_list_name"]
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 2,
            "sources": ["source_list_color"]
        },
        "target_meaning_of_life": {
            "name": "meaning_of_life",
            "data_type": "Integer",
            "sort_order": 1,
            "sources": ["source_meaning_of_life"]
        }
    }
    return target_spec, target_doc

sources = [source_nested, source_flat]
targets = [target_nested, target_flat]

def _do_test(source_spec, source_doc, target_spec, expected):
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected

# TODO Used in two files -- should be a pytest.fixture
def shuffle(to_shuffle: Dict) -> Dict:
    """Return the provided dictionary with the keys in a different order. (Since Python 3.7, key insertion order is
    preserved.)"""
    keys: List[str] = list(to_shuffle.keys())
    random.shuffle(keys)
    ret: Dict = {}
    for key in keys:
        ret[key] = to_shuffle[key]
    return ret

@pytest.mark.parametrize("source, target", itertools.product(sources, targets))
def test_folder_in_list(source, target):
    source_spec, source_doc = source()
    target_spec, expected = target()
    _do_test(source_spec, source_doc, target_spec, expected)

@pytest.mark.parametrize("source, target", itertools.product(sources, targets))
def test_folder_in_list_shuffle(source, target):
    """Verify that the folder-in-list case works even when the specs have been shuffled."""
    source_spec, source_doc = source()
    target_spec, expected = target()
    source_spec_shuffled = shuffle(source_spec)
    target_spec_shuffled = shuffle(target_spec)
    _do_test(source_spec_shuffled, source_doc, target_spec_shuffled, expected)
