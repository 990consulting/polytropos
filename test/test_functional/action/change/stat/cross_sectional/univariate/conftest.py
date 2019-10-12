from typing import Dict

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture()
def schema() -> Schema:
    temporal_spec: Dict = {
        "list_in_root": {
            "data_type": "List",
            "name": "the_list",
            "sort_order": 0
        },
        "text_in_list": {
            "data_type": "Text",
            "name": "the_text",
            "parent": "list_in_root",
            "sort_order": 0
        },
        "int_in_list": {
            "data_type": "Integer",
            "name": "the_integer",
            "parent": "list_in_root",
            "sort_order": 1
        },
        "keyed_list_in_root": {
            "data_type": "KeyedList",
            "name": "the_keyed_list",
            "sort_order": 1
        },
        "decimal_in_keyed_list": {
            "data_type": "Decimal",
            "name": "the_decimal",
            "parent": "keyed_list_in_root",
            "sort_order": 0
        },
        "text_in_keyed_list": {
            "data_type": "Text",
            "name": "the_text",
            "parent": "keyed_list_in_root",
            "sort_order": 1
        },
        "target_folder": {
            "data_type": "Folder",
            "name": "targets",
            "sort_order": 2
        },
        "target_text": {
            "data_type": "Text",
            "name": "target_text",
            "parent": "target_folder",
            "sort_order": 0
        },
        "target_int": {
            "data_type": "Integer",
            "name": "target_integer",
            "parent": "target_folder",
            "sort_order": 1
        },
        "target_decimal": {
            "data_type": "Decimal",
            "name": "target_decimal",
            "parent": "target_folder",
            "sort_order": 2
        }
    }
    temporal: Track = Track.build(temporal_spec, None, "temporal")
    immutable: Track = Track.build({}, None, "immutable")
    schema: Schema = Schema(temporal, immutable)
    return schema

@pytest.fixture()
def composite(schema) -> Composite:
    content: Dict = {
        "populated": {
            "the_list": [
                {
                    "the_text": "a",
                    "the_integer": 75
                },
                {
                    "the_text": "b",
                    "the_integer": 0
                },
                {
                    "the_text": "c",
                    "the_integer": -75
                }
            ],
            "the_keyed_list": {
                "red": {
                    "the_decimal": 0.7
                },
                "blue": {
                    "the_decimal": -24.3
                },
                "green": {
                    "the_decimal": 100.6
                }
            }

        },
        "unpopulated": {}
    }
    return Composite(schema, content)