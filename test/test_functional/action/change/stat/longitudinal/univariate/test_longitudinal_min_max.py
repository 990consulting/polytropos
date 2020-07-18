import copy
from typing import Dict, cast

import pytest

from polytropos.actions.changes.stat.longitudinal.minmax import LongitudinalMaximum, LongitudinalMinimum
from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

the_subject: VariableId = cast(VariableId, "the_subject")
the_target: VariableId = cast(VariableId, "the_target")
the_period_id: VariableId = cast(VariableId, "the_period_id")

@pytest.fixture()
def schema() -> Schema:
    temporal_spec: Dict = {
        "the_subject": {
            "name": "source",
            "data_type": "Integer",
            "sort_order": 0
        }
    }
    temporal: Track = Track.build(temporal_spec, None, "temporal")

    immutable_spec: Dict = {
        "the_target": {
            "name": "limit",
            "data_type": "Integer",
            "sort_order": 0
        },
        "the_period_id": {
            "name": "limit_period",
            "data_type": "Text",
            "sort_order": 1
        }
    }
    immutable: Track = Track.build(immutable_spec, None, "immutable")
    schema: Schema = Schema(temporal, immutable)
    return schema

@pytest.fixture()
def composite(schema) -> Composite:
    content: Dict = {
        "period_1": {},
        "period_2": {"source": 7},
        "period_3": {"source": None},
        "period_4": {"source": -1},
        "period_5": {"source": 0},
    }
    return Composite(schema, content)

def test_max(schema, composite):
    change: Change = LongitudinalMaximum(schema, {}, subject=the_subject, target=the_target,
                                         period_id_target=the_period_id)
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"] = {
        "limit": 7,
        "limit_period": "period_2"
    }
    change(composite)
    assert composite.content == expected

def test_max_no_id(schema, composite):
    change: Change = LongitudinalMaximum(schema, {}, subject=the_subject, target=the_target)
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"] = {"limit": 7}
    change(composite)
    assert composite.content == expected

def test_max_no_periods(schema, composite):
    change: Change = LongitudinalMaximum(schema, {}, subject=the_subject, target=the_target,
                                         period_id_target=the_period_id)
    composite.content = {}
    change(composite)
    assert composite.content == {}

def test_min(schema, composite):
    change: Change = LongitudinalMinimum(schema, {}, subject=the_subject, target=the_target,
                                         period_id_target=the_period_id)
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"] = {
        "limit": -1,
        "limit_period": "period_4"
    }
    change(composite)
    assert composite.content == expected
