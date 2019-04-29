import pytest
from typing import Dict, List
import random

from etl4.ontology.track import Track
from etl4.translate import Translate

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "blue_folder": {
            "apple": 75,
            "green_folder": {
                "strawberry": 102,
                "lemon": 41
            }
        },
        "orange_folder": {
            "grape": -4,
            "mango": 1,
            "papaya": None
        }
    }

@pytest.fixture()
def source_spec() -> Dict:
    return {
        "blue_folder": {
            "name": "blue_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "apple": {
            "name": "apple",
            "data_type": "Integer",
            "parent": "blue_folder",
            "sort_order": 0
        },
        "green_folder": {
            "name": "green_folder",
            "data_type": "Folder",
            "parent": "blue_folder",
            "sort_order": 1
        },
        "strawberry": {
            "name": "strawberry",
            "data_type": "Integer",
            "parent": "green_folder",
            "sort_order": 0
        },
        "lemon": {
            "name": "lemon",
            "data_type": "Integer",
            "parent": "green_folder",
            "sort_order": 1
        },
        "orange_folder": {
            "name": "orange_folder",
            "data_type": "Folder",
            "sort_order": 1
        },
        "grape": {
            "name": "grape",
            "data_type": "Integer",
            "parent": "orange_folder",
            "sort_order": 0,
        },
        "mango": {
            "name": "mango",
            "data_type": "Integer",
            "parent": "orange_folder",
            "sort_order": 1
        },
        "papaya": {
            "name": "papaya",
            "data_type": "Integer",
            "parent": "orange_folder",
            "sort_order": 2
        }
    }

@pytest.fixture()
def target_spec() -> Dict:
    return {
        "blue_folder": {
            "name": "blue_folder",
            "data_type": "Folder",
            "sort_order": 1
        },
        "apple": {
            "name": "apple",
            "data_type": "Integer",
            "sources": ["apple"],
            "parent": "blue_folder",
            "sort_order": 1
        },
        "green_folder": {
            "name": "green_folder",
            "data_type": "Folder",
            "parent": "blue_folder",
            "sort_order": 0
        },
        "strawberry": {
            "name": "strawberry",
            "data_type": "Integer",
            "sources": ["strawberry"],
            "parent": "green_folder",
            "sort_order": 0
        },
        "lemon": {
            "name": "lemon",
            "data_type": "Integer",
            "sources": ["lemon"],
            "parent": "green_folder",
            "sort_order": 1
        },
        "orange_folder": {
            "name": "orange_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "grape": {
            "name": "grape",
            "data_type": "Integer",
            "sources": ["grape"],
            "parent": "orange_folder",
            "sort_order": 1,
        },
        "mango": {
            "name": "mango",
            "data_type": "Integer",
            "sources": ["mango"],
            "parent": "orange_folder",
            "sort_order": 2
        },
        "papaya": {
            "name": "papaya",
            "data_type": "Integer",
            "sources": ["papaya"],
            "parent": "orange_folder",
            "sort_order": 0
        }
    }

@pytest.fixture()
def target_doc() -> Dict:
    return {
        "orange_folder": {
            "papaya": None,
            "grape": -4,
            "mango": 1
        },
        "blue_folder": {
            "green_folder": {
                "strawberry": 102,
                "lemon": 41
            },
            "apple": 75
        }
    }

def shuffle(to_shuffle: Dict) -> Dict:
    """Return the provided dictionary with the keys in a different order. (Since Python 3.7, key insertion order is
    preserved.)"""
    keys: List[str] = list(to_shuffle.keys())
    random.shuffle(keys)
    ret: Dict = {}
    for key in keys:
        ret[key] = to_shuffle[key]
    return ret

@pytest.mark.repeat(5)
def test_rearrange(source_doc: Dict, source_spec: Dict, target_doc: Dict, target_spec: Dict):
    """Verify that translate respects the sort order property of the variables in the target spec, and ignores the
    order in which the variables happen to be defined in the spec. """
    shuffled_source_spec = shuffle(source_spec)
    shuffled_target_spec = shuffle(target_spec)
    source_track: Track = Track.build(shuffled_source_spec, None, "Source")
    target_track: Track = Track.build(shuffled_target_spec, source_track, "Target")
    translate: Translate = Translate(target_track)
    actual: Dict = translate(source_doc)
    assert actual == target_doc
