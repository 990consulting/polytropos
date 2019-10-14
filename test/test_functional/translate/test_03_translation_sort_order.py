from collections import OrderedDict
import pytest
from typing import Dict, List, Any
import random

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator


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
        "blue_folder_source": {
            "name": "blue_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "apple_source": {
            "name": "apple",
            "data_type": "Integer",
            "parent": "blue_folder_source",
            "sort_order": 0
        },
        "green_folder_source": {
            "name": "green_folder",
            "data_type": "Folder",
            "parent": "blue_folder_source",
            "sort_order": 1
        },
        "strawberry_source": {
            "name": "strawberry",
            "data_type": "Integer",
            "parent": "green_folder_source",
            "sort_order": 0
        },
        "lemon_source": {
            "name": "lemon",
            "data_type": "Integer",
            "parent": "green_folder_source",
            "sort_order": 1
        },
        "orange_folder_source": {
            "name": "orange_folder",
            "data_type": "Folder",
            "sort_order": 1
        },
        "grape_source": {
            "name": "grape",
            "data_type": "Integer",
            "parent": "orange_folder_source",
            "sort_order": 0,
        },
        "mango_source": {
            "name": "mango",
            "data_type": "Integer",
            "parent": "orange_folder_source",
            "sort_order": 1
        },
        "papaya_source": {
            "name": "papaya",
            "data_type": "Integer",
            "parent": "orange_folder_source",
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
            "sources": ["apple_source"],
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
            "sources": ["strawberry_source"],
            "parent": "green_folder",
            "sort_order": 0
        },
        "lemon": {
            "name": "lemon",
            "data_type": "Integer",
            "sources": ["lemon_source"],
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
            "sources": ["grape_source"],
            "parent": "orange_folder",
            "sort_order": 1,
        },
        "mango": {
            "name": "mango",
            "data_type": "Integer",
            "sources": ["mango_source"],
            "parent": "orange_folder",
            "sort_order": 2
        },
        "papaya": {
            "name": "papaya",
            "data_type": "Integer",
            "sources": ["papaya_source"],
            "parent": "orange_folder",
            "sort_order": 0
        }
    }


@pytest.fixture()
def target_docs() -> List["OrderedDict[str, Any]"]:
    return [
        OrderedDict([
            ("orange_folder", OrderedDict([
                ("papaya", None),
                ("grape", -4),
                ("mango", 1)
            ])),
            ("blue_folder", OrderedDict([
                ("green_folder", OrderedDict([
                    ("strawberry", 102),
                    ("lemon", 41)
                ])),
                ("apple", 75)
            ]))
        ]),
        OrderedDict([
            ("orange_folder", OrderedDict([
                ("papaya", "papaya_source"),
                ("grape", "grape_source"),
                ("mango", "mango_source")
            ])),
            ("blue_folder", OrderedDict([
                ("green_folder", OrderedDict([
                    ("strawberry", "strawberry_source"),
                    ("lemon", "lemon_source")
                ])),
                ("apple", "apple_source")
            ]))
        ]),
    ]


def shuffle(to_shuffle: Dict) -> Dict:
    """Return the provided dictionary with the keys in a different order. (Since Python 3.7, key insertion order is
    preserved.)"""
    keys: List[str] = list(to_shuffle.keys())
    random.shuffle(keys)
    ret: Dict = {}
    for key in keys:
        ret[key] = to_shuffle[key]
    return ret


@pytest.mark.parametrize(
    "index, create_document_value_provider", enumerate([DocumentValueProvider, TraceDocumentValueProvider])
)
@pytest.mark.repeat(5)
def test_rearrange(source_doc: Dict, source_spec: Dict, target_docs: List[Dict], target_spec: Dict, index, create_document_value_provider):
    """Verify that translate respects the sort order property of the variables in the target spec, and ignores the
    order in which the variables happen to be defined in the spec. """
    shuffled_source_spec = shuffle(source_spec)
    shuffled_target_spec = shuffle(target_spec)
    source_track: Track = Track.build(shuffled_source_spec, None, "Source")
    target_track: Track = Track.build(shuffled_target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == target_docs[index]
