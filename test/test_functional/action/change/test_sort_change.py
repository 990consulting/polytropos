import copy
from datetime import datetime
from collections import OrderedDict
from typing import Callable, Dict, List, Optional, Any

import pytest
from polytropos.ontology.composite import Composite

from polytropos.actions.changes.sort import Sort
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
import random

from polytropos.ontology.variable import Variable

class Shuffle:
    """Inverse of sort -- completely randomize all structure to be sorted"""
    def __init__(self, schema: Schema):
        self.schema = schema

    def _shuffle_within_keyed_list(self, to_shuffle: Dict, path: List) -> Dict:
        ret: Dict[str, Dict] = OrderedDict()
        for key, value in to_shuffle.items():
            ret[key] = self._shuffle_within_folder(value, path)
        return ret

    def _shuffle_within_list(self, to_shuffle: List, path: List) -> List:
        ret: List = [None] * len(to_shuffle)
        for i, child in enumerate(to_shuffle):
            ret[i] = self._shuffle_within_folder(child, path)
        return ret

    def _shuffle_within_folder(self, to_shuffle: Optional[Dict], path: List) -> Optional[Dict]:
        if to_shuffle is None:
            return None
        ret: OrderedDict = OrderedDict()
        keys: List[str] = list(to_shuffle.keys())
        random.shuffle(keys)
        for key in keys:
            value: Optional[Any] = to_shuffle[key]
            key_path = path + [key]
            var: Optional[Variable] = self.schema.lookup(key_path)
            if var is None:
                ret[key] = value
            elif value is not None and var.data_type == "Folder":
                ret[key] = self._shuffle_within_folder(value, key_path)
            elif value is not None and var.data_type == "List":
                ret[key] = self._shuffle_within_list(value, key_path)
            elif value is not None and var.data_type == "KeyedList":
                ret[key] = self._shuffle_within_keyed_list(value, key_path)
            else:
                ret[key] = value
        return ret

    def __call__(self, to_shuffle: Dict) -> Dict:
        ret = OrderedDict()
        keys: List[str] = list(to_shuffle.keys())
        random.shuffle(keys)
        for key in keys:
            ret[key] = self._shuffle_within_folder(to_shuffle[key], [])
        return ret

@pytest.fixture()
def make_track() -> Callable:
    def _make_track(name: str) -> Track:
        spec: Dict = {
            "%s_text_in_root" % name: {
                "name": "%s_text_in_root" % name,
                "sort_order": 0,
                "data_type": "Text"
            },
            "%s_folder_in_root" % name: {
                "name": "%s_folder_in_root" % name,
                "sort_order": 1,
                "data_type": "Folder"
            },
            "%s_text_in_folder_in_root" % name: {
                "name": "some_text",
                "sort_order": 0,
                "parent": "%s_folder_in_root" % name,
                "data_type": "Text"
            },
            "%s_multitext_in_folder_in_root" % name: {
                "name": "some_multitext",
                "sort_order": 1,
                "parent": "%s_folder_in_root" % name,
                "data_type": "MultipleText"
            },
            "%s_list_in_folder_in_root" % name: {
                "name": "some_list",
                "sort_order": 2,
                "parent": "%s_folder_in_root" % name,
                "data_type": "List"
            },
            "%s_some_int_in_list_in_folder_in_root" % name: {
                "name": "some_int",
                "sort_order": 0,
                "parent": "%s_list_in_folder_in_root" % name,
                "data_type": "Integer"
            },
            "%s_some_date_in_list_in_folder_in_root" % name: {
                "name": "some_date",
                "sort_order": 1,
                "parent": "%s_list_in_folder_in_root" % name,
                "data_type": "Date"
            },
            "%s_keyed_list_in_root" % name: {
                "name": "%s_keyed_list_in_root" % name,
                "sort_order": 2,
                "data_type": "KeyedList"
            },
            "%s_decimal_in_keyed_list_in_root" % name: {
                "name": "some_decimal",
                "sort_order": 0,
                "parent": "%s_keyed_list_in_root" % name,
                "data_type": "Decimal"
            },
            "%s_currency_in_keyed_list_in_root" % name: {
                "name": "some_currency",
                "sort_order": 1,
                "parent": "%s_keyed_list_in_root" % name,
                "data_type": "Currency"
            }
        }
        track: Track = Track.build(spec, None, name)
        return track
    return _make_track

@pytest.fixture()
def schema(make_track) -> Schema:
    temporal: Track = make_track("temporal")
    immutable: Track = make_track("immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def content() -> Dict:
    return OrderedDict([
        ("201012", OrderedDict([
            ("not_part_of_schema", None),
            ("temporal_text_in_root", "B"),
            ("temporal_folder_in_root", OrderedDict([
                ("some_text", "B"),
                ("some_multitext", ["C", "D", "E"]),
                ("some_list", [
                    OrderedDict([
                        ("some_int", 1),
                        ("some_date", "2000-01-01")
                    ]),
                    OrderedDict([
                        ("some_int", 2),
                        ("some_date", "2001-01-01")
                    ])
                ])
            ]))
        ])),
        ("201112", OrderedDict([
            ("NOT PART OF SCHEMA", None),
            ("temporal_text_in_root", "F"),
            ("temporal_folder_in_root", OrderedDict([
                ("some_text", "G"),
                ("some_multitext", ["H", "I", "J"])
            ])),
            ("temporal_keyed_list_in_root", {
                "FF": {
                    "some_decimal": -12.5,
                    "some_currency": -15
                },
                "GG": {
                    "some_decimal": -17.5,
                    "sume_currency": -115
                }
            })
        ])),
        ("201312", OrderedDict([
            ("not in schema", 5),
            ("temporal_folder_in_root", None)
        ])),
        ("immutable", OrderedDict([
            ("i_NOT PART OF SCHEMA", None),
            ("immutable_text_in_root", "K"),
            ("immutable_folder_in_root", OrderedDict([
                ("NOT IN SCHEMA", "xyz"),
                ("some_text", "L"),
                ("some_multitext", ["M", "N", "O"]),
                ("some_list", [
                    OrderedDict([
                        ("some_int", 5),
                        ("some_date", "2004-01-01")
                    ]),
                    OrderedDict([
                        ("some_int", 6),
                        ("some_date", "2005-01-01")
                    ])
                ])
            ])),
            ("immutable_keyed_list_in_root", {
                "FFF": {
                    "some_decimal": -112.5,
                    "some_currency": -115
                },
                "GGG": {
                    "some_decimal": -117.5,
                    "sume_currency": -1115
                }
            })
         ]))
    ])

"""
def content() -> Dict:
    return {
        "201012": {
            "not_part_of_schema": None,
            "temporal_text_in_root": "A",
            "temporal_folder_in_root": {
                "some_text": "B",
                "some_multitext": ["C", "D", "E"],
                "some_list": [
                    {
                        "some_int": 1,
                        "some_date": "2000-01-01"
                    },
                    {
                        "some_int": 2,
                        "some_date": "2001-01-01"
                    }
                ]
            }
        },
        "201112": {
            "NOT_PART_OF_SCHEMA": None,
            "temporal_text_in_root": "F",
            "temporal_folder_in_root": {
                "some_text": "G",
                "some_multitext": ["H", "I", "J"],
            },
            "temporal_keyed_list_in_root": {
                "FF": {
                    "some_decimal": -12.5,
                    "some_currency": -15
                },
                "GG": {
                    "some_decimal": -17.5,
                    "sume_currency": -115
                }
            }
        },
        "201312": {
            "not in schema": 5,
            "temporal_folder_in_root": None
        },
        "immutable": {
            "i_NOT PART OF SCHEMA": None,
            "immutable_text_in_root": "K",
            "immutable_folder_in_root": {
                "NOT IN SCHEMA": "xyz",
                "some_text": "L",
                "some_multitext": ["M", "N", "O"],
                "some_list": [
                    {
                        "some_int": 5,
                        "some_date": "2004-01-01"
                    },
                    {
                        "some_int": 6,
                        "some_date": "2005-01-01"
                    }
                ]
            },
            "immutable_keyed_list_in_root": {
                "FFF": {
                    "some_decimal": -112.5,
                    "some_currency": -115
                },
                "GGG": {
                    "some_decimal": -117.5,
                    "sume_currency": -1115
                }
            }
        }
    }
"""

@pytest.mark.parametrize("_", range(5))
def test_sort_change(schema, content, _):
    random.seed(datetime.now())
    expected: Dict = copy.deepcopy(content)
    shuffle: Shuffle = Shuffle(schema)
    shuffled: Dict = shuffle(content)
    sort: Sort = Sort(schema, {})
    composite: Composite = Composite(schema, shuffled)
    sort(composite)
    assert composite.content == expected