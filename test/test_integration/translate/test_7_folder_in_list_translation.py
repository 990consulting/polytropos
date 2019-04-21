import random

import pytest
from typing import Dict, Tuple, List
from etl4.ontology.track import Track
from etl4.translate import Translate
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
            "type": "List",
            "sort_order": 0
        },
        "source_list_day": {
            "name": "day",
            "type": "Text",
            "parent": "source_list",
            "sort_order": 0
        },
        "source_list_folder": {
            "name": "the_folder",
            "type": "Folder",
            "parent": "source_list",
            "sort_order": 1
        },
        "source_list_name": {
            "name": "name",
            "type": "Text",
            "parent": "source_list_folder",
            "sort_order": 0
        },
        "source_list_color": {
            "name": "color",
            "type": "Text",
            "parent": "source_list_folder",
            "sort_order": 1
        },
        "source_meaning_of_life": {
            "name": "meaning_of_life",
            "type": "Integer",
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
            "type": "List",
            "sort_order": 0
        },
        "source_list_day": {
            "name": "day",
            "type": "Text",
            "parent": "source_list",
            "sort_order": 0
        },
        "source_list_name": {
            "name": "name",
            "type": "Text",
            "parent": "source_list",
            "sort_order": 1
        },
        "source_list_color": {
            "name": "color",
            "type": "Text",
            "parent": "source_list",
            "sort_order": 2
        },
        "source_meaning_of_life": {
            "name": "meaning_of_life",
            "type": "Integer",
            "sort_order": 1
        }
    }
    return source_spec, source_doc

def target_nested() -> Tuple[Dict, Dict]:
    target_doc: Dict = {
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

    target_spec: Dict = {
        "target_list": {
            "name": "the_list",
            "type": "List",
            "sort_order": 0,
            "sources": ["source_list"],
            "source_child_mappings": {
                "source_list": {
                    "target_list_name": ["source_list_name"],
                    "target_list_color": ["source_list_color"]
                }
            }
        },
        "target_list_day": {
            "name": "day",
            "type": "Text",
            "parent": "target_list",
            "sort_order": 0
        },
        "target_list_folder": {
            "name": "the_folder",
            "type": "Folder",
            "parent": "target_list",
            "sort_order": 1
        },
        "target_list_name": {
            "name": "name",
            "type": "Text",
            "parent": "target_list_folder",
            "sort_order": 0
        },
        "target_list_color": {
            "name": "color",
            "type": "Text",
            "parent": "target_list_folder",
            "sort_order": 1
        },
        "target_meaning_of_life": {
            "name": "meaning_of_life",
            "type": "Integer",
            "sort_order": 1,
            "sources": ["source_meaning_of_life"]
        }
    }
    return target_spec, target_doc

def target_flat() -> Tuple[Dict, Dict]:
    target_doc: Dict = {
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

    target_spec: Dict = {
        "target_list": {
            "name": "the_list",
            "type": "List",
            "sort_order": 0,
            "sources": ["source_list"],
            "source_child_mappings": {
                "source_list": {
                    "target_list_name": ["source_list_name"],
                    "target_list_color": ["source_list_color"]
                }
            }
        },
        "target_list_day": {
            "name": "day",
            "type": "Text",
            "parent": "target_list",
            "sort_order": 0
        },
        "target_list_name": {
            "name": "name",
            "type": "Text",
            "parent": "target_list",
            "sort_order": 1
        },
        "target_list_color": {
            "name": "color",
            "type": "Text",
            "parent": "target_list",
            "sort_order": 2
        },
        "target_meaning_of_life": {
            "name": "meaning_of_life",
            "type": "Integer",
            "sort_order": 1,
            "sources": ["source_meaning_of_life"]
        }
    }
    return target_spec, target_doc

sources = [source_nested, source_flat]
targets = [target_nested, target_flat]

def _do_test(source_spec, source_doc, target_spec, expected):
    source_track: Track = Track.build(source_spec)
    target_track: Track = Track.build(target_spec)
    translate: Translate = Translate(source_track, target_track)
    actual: Dict = translate(source_doc)
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
