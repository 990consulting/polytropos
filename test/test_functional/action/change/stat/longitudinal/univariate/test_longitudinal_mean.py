import copy
from typing import Dict, Callable, cast

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.actions.changes.stat.longitudinal.reduce import LongitudinalMean
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def schema() -> Schema:
    temporal_spec: Dict = {
        "integer_source": {
            "name": "integer_source",
            "data_type": "Integer",
            "sort_order": 0
        },
        "decimal_source": {
            "name": "decimal_source",
            "data_type": "Decimal",
            "sort_order": 1
        },
        "currency_source": {
            "name": "currency_source",
            "data_type": "Currency",
            "sort_order": 2
        }
    }
    immutable_spec: Dict = {
        "target": {
            "name": "target",
            "data_type": "Decimal",
            "sort_order": 0
        }
    }
    temporal: Track = Track(temporal_spec, None, "temporal")
    immutable: Track = Track(immutable_spec, None, "immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def do_test(schema) -> Callable:
    def _do_test(content: Dict, source: VariableId, expected: Dict) -> None:
        composite: Composite = Composite(schema, content)
        target: VariableId = cast(VariableId, "target")
        change: LongitudinalMean = LongitudinalMean(schema, {}, source, target)
        change(composite)
        assert composite.content == expected

    return _do_test

@pytest.mark.parametrize("source", ["integer_source", "decimal_source", "currency_source"])
def test_no_periods(do_test: Callable, source: str):
    content: Dict = {}
    expected: Dict = {
        "immutable": {
            "target": None
        }
    }
    source_id: VariableId = cast(VariableId, source)
    do_test(content, source_id, expected)

@pytest.mark.parametrize("source", ["integer_source", "decimal_source", "currency_source"])
def test_no_observations(do_test: Callable, source: str):
    source_id: VariableId = cast(VariableId, source)
    content: Dict = {
        "period_1": {},
        "period_2": {},
        "period_3": {}
    }
    expected: Dict = copy.deepcopy(content)
    expected["immutable"] = {"target": None}
    do_test(content, source_id, expected)

@pytest.mark.parametrize("source", ["integer_source", "currency_source"])
def test_int_like_source(do_test: Callable, source: str):
    source_id: VariableId = cast(VariableId, source)
    content: Dict = {
        "period_1": {
            source: 5
        },
        "period_2": {
            source: 2
        },
        "period_3": {
            source: 11
        }
    }
    expected: Dict = copy.deepcopy(content)
    expected["immutable"] = {"target": 6.0}
    do_test(content, source_id, expected)

def test_decimal_source(do_test: Callable):
    source: str = "decimal_source"
    source_id: VariableId = cast(VariableId, source)
    content: Dict = {
        "period_1": {
            source: 0.5
        },
        "period_2": {
            source: 0.2
        },
        "period_3": {
            source: 1.1
        }
    }
    expected: Dict = copy.deepcopy(content)
    expected["immutable"] = {"target": 0.6}
    do_test(content, source_id, expected)