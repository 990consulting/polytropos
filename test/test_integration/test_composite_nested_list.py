"""The primary purpose of this "test" is to demonstrate how to work with nested lists in Polytropos."""

import pytest
from typing import Dict, Tuple, List

from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture
def nested_list_schema() -> Schema:
    immutable_spec: Dict = {
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
        }
    }

    immutable_track: Track = Track.build(immutable_spec, None, "immutable")
    temporal_track: Track = Track.build({}, None, "Temporal")
    schema: Schema = Schema(temporal_track, immutable_track)
    return schema

@pytest.fixture
def nested_list_composite(nested_list_schema) -> Composite:
    content: Dict = {
        "immutable": {
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
            ]
        }
    }

    return Composite(nested_list_schema, content)

@pytest.fixture
def parallel_repr() -> List:
    return [
        {
            "inner": [
                {"nombre": "inner_1_1_1"},
                {"nombre": "inner_1_1_2"}
            ]
        }, {
            "inner": [
                {"nombre": "inner_1_2_1"},
                {"nombre": "inner_1_2_2"}
            ]
        }
    ]

@pytest.fixture
def unusual_repr() -> List:
    return [
        [
            {"nombre": "inner_1_1_1"},
            {"nombre": "inner_1_1_2"}
        ], [
            {"nombre": "inner_1_2_1"},
            {"nombre": "inner_1_2_2"}
        ]
    ]

@pytest.fixture
def decode_mapping() -> Dict[str, str]:
    return {
        "outer_list_1_id": "outer",
        "inner_list_1_id": "inner",
        "name_1_id": "nombre"
    }

@pytest.fixture
def encode_mapping() -> Dict[str, str]:
    return {
        "outer": "outer_list_1_id",
        "inner": "inner_list_1_id",
        "nombre": "name_1_id"
    }

"""
Remember: encode and decode don't directly use the content of the composite, although an upstream or downstream
step will probably read/write content from the composite based on the encoding/decoding. 
"""

def test_encode_parallel_structure_scenario(nested_list_composite, nested_list_schema, encode_mapping, parallel_repr):
    """Scenario 1: The structure of the schema list is identical to the structure of the internal list, but with
    different labels."""

    target: Composite = Composite(nested_list_schema, {})

    # First application: encode the innermost items so that they match the schema. Notice that we hard-code the internal
    # representation, which is the point of the encode/decode scheme--Polytropos actions can make use of any internal
    # representation and still be agnostic to the final, external representation.
    outer: List = []
    for item in parallel_repr:  # type: Dict
        inner = item["inner"]  # The calling method must be aware of its own internal structures
        inner_elements_encoded = list(target.encode_list(encode_mapping, inner))
        inner_item_encoded = {
            "inner": inner_elements_encoded
        }
        outer.append(inner_item_encoded)

    # Second application: Treating the inner content as a black box, encode it into the outer represenation.
    outer_encoded: List[Dict] = list(nested_list_composite.encode_list(encode_mapping, outer))
    target.put_immutable("outer_list_1_id", outer_encoded)
    assert target.content == nested_list_composite.content

def test_encode_non_canonical_structure(nested_list_composite, nested_list_schema, encode_mapping, unusual_repr):
    """Scenario 2: The incoming data does not have the structure expected by Polytropos."""
    target: Composite = Composite(nested_list_schema, {})

    outer: List = []
    for inner in unusual_repr:  # type: List
        inner_elements_encoded = list(target.encode_list(encode_mapping, inner))
        inner_item_encoded = {
            "inner": inner_elements_encoded
        }
        outer.append(inner_item_encoded)

    outer_encoded: List[Dict] = list(nested_list_composite.encode_list(encode_mapping, outer))
    target.put_immutable("outer_list_1_id", outer_encoded)
    assert target.content == nested_list_composite.content

def test_decode_list_parallel_structure(nested_list_composite, decode_mapping, parallel_repr):
    """Reverse equivalent encode scenario."""
    outer_encoded = list(nested_list_composite.get_immutable("outer_list_1_id"))
    outer = list(nested_list_composite.decode_list(decode_mapping, outer_encoded))
    outer_decoded: List = []
    for item in outer:
        inner_decoded = list(nested_list_composite.decode_list(decode_mapping, item["inner"]))
        inner_item = {
            "inner": inner_decoded
        }
        outer_decoded.append(inner_item)
    assert outer_decoded == parallel_repr

def test_decode_list_non_canonical_structure(nested_list_composite, decode_mapping, unusual_repr):
    """Reverse equivalent encode scenario."""
    outer_encoded = list(nested_list_composite.get_immutable("outer_list_1_id"))
    outer = list(nested_list_composite.decode_list(decode_mapping, outer_encoded))
    outer_decoded: List = []
    for item in outer:
        inner_decoded = list(nested_list_composite.decode_list(decode_mapping, item["inner"]))
        outer_decoded.append(inner_decoded)
    assert outer_decoded == unusual_repr

