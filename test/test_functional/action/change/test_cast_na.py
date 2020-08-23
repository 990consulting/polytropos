"""Verify that Translate will accept an arbitrary list of strings to be treated as equivalent to None."""

from typing import Dict, Callable, List, Set

import pytest

from polytropos.actions.changes.cast import Cast
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track


@pytest.fixture()
def schema() -> Schema:
    spec: Dict = {
        "the_var": {
            "name": "the_var",
            "data_type": "Integer",
            "sort_order": 0
        }
    }
    temporal: Track = Track.build({}, None, "temporal")
    immutable: Track = Track.build(spec, None, "immutable")
    return Schema(temporal, immutable, "Schema")

@pytest.fixture()
def make_cast(schema) -> Callable:
    def _make_cast(na_values: Set[str]) -> Cast:
        return Cast(schema, {}, na_values)
    return _make_cast

@pytest.fixture()
def make_composite(schema) -> Callable:
    def _make_composite(value: str) -> Composite:
        content: Dict = {
            "immutable": {
                "the_var": value
            }
        }
        return Composite(schema, content)
    return _make_composite

@pytest.mark.parametrize("source_value", ["NA", "RESTRICTED", None])
def test_translate_with_valid_na(make_cast, source_value, make_composite):
    cast: Cast = make_cast({"NA", "RESTRICTED"})
    composite: Composite = make_composite(source_value)
    expected: Dict = {
        "immutable": {
            "the_var": None
        }
    }
    cast(composite)
    assert composite.content == expected

@pytest.mark.parametrize("source_value", ["na", "restricted"])
def test_translate_with_invalid_na(make_cast, source_value, make_composite):
    cast: Cast = make_cast({"NA", "RESTRICTED"})
    composite: Composite = make_composite(source_value)
    expected: Dict = {
        "immutable": {
            "qc": {
                "_exceptions": {
                    "cast_errors": {
                        "the_var": source_value
                    }
                }
            }
        }
    }
    cast(composite)
    assert composite.content == expected

@pytest.mark.parametrize("source_value", ["NA", "RESTRICTED"])
def test_translate_with_no_na(make_cast, source_value, make_composite):
    cast: Cast = make_cast({})
    composite: Composite = make_composite(source_value)
    expected: Dict = {
        "immutable": {
            "qc": {
                "_exceptions": {
                    "cast_errors": {
                        "the_var": source_value
                    }
                }
            }
        }
    }
    cast(composite)
    assert composite.content == expected
