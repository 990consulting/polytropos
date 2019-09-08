from collections import Callable
from typing import Dict, Iterable, List

import pytest

from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track

@pytest.fixture()
def make_track() -> Callable:
    def _make_track(prefix: str) -> Track:
        spec: Dict = {}
        for i, data_type in enumerate(["Text", "Integer", "Decimal", "Currency", "Date"]):
            lc_dt: str = data_type.lower()
            key: str = "%s_%s" % (prefix, lc_dt)
            spec[key] = {
                "name": key,
                "data_type": data_type,
                "sort_order": i
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
            "t_text": "f",
            "t_integer": 10,
            "t_decimal": 3.14,
            "t_currency": 100.75,
            "t_date": "2016-05-01"
        },
        "period_2": {
            "t_text": "B",
            "t_integer": -10,
            "t_decimal": 0.7,
            "t_currency": 32,
            "t_date": "1984-05-01"
        },
        "period_3": {},
        "immutable": {
            "i_text": "x",
            "i_integer": 0,
            "i_decimal": 0.0,
            "i_currency": -1e7,
            "i_date": "2001-06-05"
        }
    }
    return Composite(schema, content, composite_id="composite_1")

@pytest.fixture()
def composite_2(schema) -> Composite:
    content: Dict = {
        "period_1": {
            "t_text": "h",
            "t_integer": 4,
            "t_decimal": 37.5,
            "t_currency": 1.0,
            "t_date": "2010-08-01"
        }
    }
    return Composite(schema, content, composite_id="composite_2")

@pytest.fixture()
def composites(composite_1, composite_2) -> List[Composite]:
    return [composite_1, composite_2]
