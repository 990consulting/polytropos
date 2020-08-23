"""Verify that Translate will accept an arbitrary list of strings to be treated as equivalent to None."""
import copy
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
            "data_type": "MultipleText",
            "sort_order": 0
        }
    }
    temporal: Track = Track.build({}, None, "temporal")
    immutable: Track = Track.build(spec, None, "immutable")
    return Schema(temporal, immutable, "Schema")

@pytest.mark.parametrize("value", [
    ["A", "B", "C"],
    [],
    None,
    "This is actually invalid, but it shouldn't have an effect"
])
def test_cast_ignores_multiple_text(schema, value):
    content: Dict = {
        "immutable": {
            "the_var": value
        }
    }
    expected: Dict = copy.deepcopy(content)
    composite: Composite = Composite(schema, content)
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.content == expected