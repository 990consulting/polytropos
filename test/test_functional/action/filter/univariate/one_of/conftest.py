from collections import Callable
from typing import Dict, List

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track

@pytest.fixture()
def make_track() -> Callable:
    def _make_track(prefix: str) -> Track:
        key: str = "%s_text" % prefix
        spec: Dict = {
            key: {
                "name": key,
                "data_type": "Text",
                "sort_order": 0
            }
        }
        return Track(spec, None, prefix)
    return _make_track

@pytest.fixture()
def schema(make_track) -> Schema:
    immutable: Track = make_track("i")
    temporal: Track = make_track("t")
    return Schema(temporal, immutable)

@pytest.fixture()
def composite_1(schema) -> Composite:
    content: Dict = {
        "period_1": {
            "t_text": "abc"
        },
        "period_2": {
            "t_text": "DEF"
        },
        "immutable": {
            "i_text": "ghI"
        }
    }
    return Composite(schema, content)

@pytest.fixture()
def composite_2(schema) -> Composite:
    content: Dict = {
        "period_1": {
            "t_text": "012"
        },
        "period_2": {
            "t_text": "345"
        },
        "immutable": {
            "t_text": "678"
        }
    }
    return Composite(schema, content)

@pytest.fixture()
def composites(composite_1, composite_2) -> List[Composite]:
    return [composite_1, composite_2]
