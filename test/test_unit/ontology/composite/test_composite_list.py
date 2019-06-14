"""Test methods that encode and decode lists. These methods do not actually care about the content of the composite
itself, but only its schema; they take content as an argument and return the same content in a different
representation."""

from typing import List, Dict

import pytest

from polytropos.ontology.composite import Composite

@pytest.fixture
def encode_mapping() -> Dict:
    return {
        "name": "source_root_2_nombre",
        "age": "source_root_2_edad",
        "ice cream": "source_root_2_helado"
    }

@pytest.fixture
def decode_mapping() -> Dict:
    return {
        "source_root_2_nombre": "name",
        "source_root_2_edad": "age",
        "source_root_2_helado": "ice cream"
    }

def test_encode_list_trivial(trivial_schema):
    """No mappings, no content"""
    composite = Composite(trivial_schema)
    actual: List = list(composite.encode_list({}, []))
    assert actual == []

def test_encode_list_zero_length(immutable_list_schema, encode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_list_schema)
    actual: List = list(composite.encode_list(encode_mapping, []))
    assert actual == []

def test_encode_list_multiple_empty(immutable_list_schema, encode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_list_schema)
    content: List[Dict] = [{}, {}, {}]
    expected: List = content.copy()
    actual: List = list(composite.encode_list(encode_mapping, content))
    assert actual == expected

def test_encode_list(immutable_list_schema, encode_mapping):
    """Both mappings and content present."""
    composite = Composite(immutable_list_schema)
    content: List[Dict] = [
        {
            "name": "Al",
            "age": 25,
            "ice cream": "Rocky road"
        }, {
            "name": "Joe",
            "age": 34,
            "ice cream": "Clam chowder"   # https://now.tufts.edu/articles/dish-we-all-scream-for-ice-cream
        }
    ]
    expected: List = [
        {
            "inner_folder": {
                "nombre": "Al",
                "edad": 25
            },
            "helado": "Rocky road"
        },
        {
            "inner_folder": {
                "nombre": "Joe",
                "edad": 34
            },
            "helado": "Clam chowder"
        }
    ]
    actual: List = list(composite.encode_list(encode_mapping, content))
    assert actual == expected

def test_encode_unmapped_content_raises(immutable_list_schema, encode_mapping):
    """If a content list item contains a field without a mapping, raise."""
    composite = Composite(immutable_list_schema)
    content: List[Dict] = [{"unknown_field": "foo"}]
    with pytest.raises(ValueError):
        # Wrap in list to force lazy execution
        list(composite.encode_list(encode_mapping, content))

def test_encode_missing_content_skips(immutable_list_schema, encode_mapping):
    """If something isn't present in a content list item that is defined in the mappings, skip it."""
    composite = Composite(immutable_list_schema)
    content: List[Dict] = [
        {
            "ice cream": "Rocky road"
        }, {
            "name": "Joe",
        }
    ]
    expected: List = [
        {
            "helado": "Rocky road"
        },
        {
            "inner_folder": {
                "nombre": "Joe"
            }
        }
    ]
    actual: List = list(composite.encode_list(encode_mapping, content))
    assert actual == expected

def test_encode_null_content(immutable_list_schema, encode_mapping):
    """Content that is explicitly null is encoded."""
    composite = Composite(immutable_list_schema)
    content: List[Dict] = [{"name": None}]
    expected: List = [
        {
            "inner_folder": {
                "nombre": None
            }
        }
    ]
    actual: List = list(composite.encode_list(encode_mapping, content))
    assert actual == expected

def test_decode_list_trivial(trivial_schema):
    """No mappings, no content"""
    composite = Composite(trivial_schema)
    actual: List = list(composite.decode_list({}, []))
    assert actual == []

def test_decode_list_zero_length(immutable_list_schema, decode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_list_schema)
    actual: List = list(composite.decode_list(decode_mapping, []))
    assert actual == []

def test_decode_list_multiple_empty(immutable_list_schema, decode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_list_schema)
    content: List[Dict] = [{}, {}, {}]
    expected: List = content.copy()
    actual: List = list(composite.decode_list(decode_mapping, content))
    assert actual == expected

def test_decode_list(immutable_list_schema, decode_mapping):
    """Both mappings and content present."""
    composite = Composite(immutable_list_schema)
    content: List = [
        {
            "inner_folder": {
                "nombre": "Al",
                "edad": 25
            },
            "helado": "Rocky road"
        },
        {
            "inner_folder": {
                "nombre": "Joe",
                "edad": 34
            },
            "helado": "Clam chowder"
        }
    ]
    expected: List[Dict] = [
        {
            "name": "Al",
            "age": 25,
            "ice cream": "Rocky road"
        }, {
            "name": "Joe",
            "age": 34,
            "ice cream": "Clam chowder"   # https://now.tufts.edu/articles/dish-we-all-scream-for-ice-cream
        }
    ]
    actual: List = list(composite.decode_list(decode_mapping, content))
    assert actual == expected

def test_decode_missing_content_skips(immutable_list_schema, decode_mapping):
    """If something isn't present in a content list item that is defined in the mappings, skip it."""
    composite = Composite(immutable_list_schema)
    content: List = [
        {
            "helado": "Rocky road"
        },
        {
            "inner_folder": {
                "nombre": "Joe"
            }
        }
    ]
    expected: List[Dict] = [
        {
            "ice cream": "Rocky road"
        }, {
            "name": "Joe",
        }
    ]
    actual: List = list(composite.decode_list(decode_mapping, content))
    assert actual == expected

def test_decode_null_content(immutable_list_schema, decode_mapping):
    """Content that is explicitly null is decoded."""
    composite = Composite(immutable_list_schema)
    content: List = [
        {
            "inner_folder": {
                "nombre": None
            }
        }
    ]
    expected: List[Dict] = [{"name": None}]
    actual: List = list(composite.decode_list(decode_mapping, content))
    assert actual == expected

