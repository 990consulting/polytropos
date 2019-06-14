"""Test methods that encode and decode named lists. These methods do not actually care about the content of the
composite itself, but only its schema; they take content as an argument and return the same content in a different
representation. """
import copy
from typing import Dict

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
    actual: Dict = composite.encode_named_list({}, {})
    assert actual == {}

def test_encode_named_list_zero_length(immutable_named_list_schema, encode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_named_list_schema)
    actual: Dict = composite.encode_named_list(encode_mapping, {})
    assert actual == {}

def test_encode_named_list_multiple_empty(immutable_named_list_schema, encode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "tom": {},
        "dick": {},
        "harry": {}
    }
    expected: Dict = copy.deepcopy(content)
    actual: Dict = composite.encode_named_list(encode_mapping, content)
    assert actual == expected

def test_encode_named_list(immutable_named_list_schema, encode_mapping):
    """Both mappings and content present."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "al": {
            "name": "Al",
            "age": 25,
            "ice cream": "Rocky road"
        },
        "joe": {
            "name": "Joe",
            "age": 34,
            "ice cream": "Clam chowder"   # https://now.tufts.edu/articles/dish-we-all-scream-for-ice-cream
        }
    }
    expected: Dict = {
        "al": {
            "inner_folder": {
                "nombre": "Al",
                "edad": 25
            },
            "helado": "Rocky road"
        },
        "joe": {
            "inner_folder": {
                "nombre": "Joe",
                "edad": 34
            },
            "helado": "Clam chowder"
        }
    }
    actual: Dict = composite.encode_named_list(encode_mapping, content)
    assert actual == expected

def test_encode_unmapped_content_raises(immutable_named_list_schema, encode_mapping):
    """If a content list item contains a field without a mapping, raise."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {"x": {"unknown_field": "foo"}}
    with pytest.raises(ValueError):
        composite.encode_named_list(encode_mapping, content)

def test_encode_missing_content_skips(immutable_named_list_schema, encode_mapping):
    """If something isn't present in a content list item that is defined in the mappings, skip it."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "al": {
            "ice cream": "Rocky road"
        },
        "joe": {
            "name": "Joe",
        }
    }
    expected: Dict = {
        "al": {
            "helado": "Rocky road"
        },
        "joe": {
            "inner_folder": {
                "nombre": "Joe"
            }
        }
    }
    actual: Dict = composite.encode_named_list(encode_mapping, content)
    assert actual == expected

def test_encode_null_content(immutable_named_list_schema, encode_mapping):
    """Content that is explicitly null is encoded."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {"x": {"name": None}}
    expected: Dict = {
        "x": {
            "inner_folder": {
                "nombre": None
            }
        }
    }
    actual: Dict = composite.encode_named_list(encode_mapping, content)
    assert actual == expected

def test_decode_named_list_trivial(trivial_schema):
    """No mappings, no content"""
    composite = Composite(trivial_schema)
    actual: Dict = composite.decode_named_list({}, {})
    assert actual == {}

def test_decode_named_list_zero_length(immutable_named_list_schema, decode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_named_list_schema)
    actual: Dict = composite.decode_named_list(decode_mapping, {})
    assert actual == {}

def test_decode_named_list_multiple_empty(immutable_named_list_schema, decode_mapping):
    """Mappings present, no content."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "x": {},
        "y": {},
        "z": {}
    }
    expected: Dict = content.copy()
    actual: Dict = composite.decode_named_list(decode_mapping, content)
    assert actual == expected

def test_decode_named_list(immutable_named_list_schema, decode_mapping):
    """Both mappings and content present."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "al": {
            "inner_folder": {
                "nombre": "Al",
                "edad": 25
            },
            "helado": "Rocky road"
        },
        "joe": {
            "inner_folder": {
                "nombre": "Joe",
                "edad": 34
            },
            "helado": "Clam chowder"
        }
    }
    expected: Dict = {
        "al": {
            "name": "Al",
            "age": 25,
            "ice cream": "Rocky road"
        },
        "joe": {
            "name": "Joe",
            "age": 34,
            "ice cream": "Clam chowder"   # https://now.tufts.edu/articles/dish-we-all-scream-for-ice-cream
        }
    }
    actual: Dict = composite.decode_named_list(decode_mapping, content)
    assert actual == expected

def test_decode_missing_content_skips(immutable_named_list_schema, decode_mapping):
    """If something isn't present in a content list item that is defined in the mappings, skip it."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "al": {
            "helado": "Rocky road"
        },
        "joe": {
            "inner_folder": {
                "nombre": "Joe"
            }
        }
    }
    expected: Dict = {
        "al": {
            "ice cream": "Rocky road"
        },
        "joe": {
            "name": "Joe",
        }
    }
    actual: Dict = composite.decode_named_list(decode_mapping, content)
    assert actual == expected

def test_decode_null_content(immutable_named_list_schema, decode_mapping):
    """Content that is explicitly null is decoded."""
    composite = Composite(immutable_named_list_schema)
    content: Dict = {
        "x": {
            "inner_folder": {
                "nombre": None
            }
        }
    }
    expected: Dict = {"x": {"name": None}}
    actual: Dict = composite.decode_named_list(decode_mapping, content)
    assert actual == expected

