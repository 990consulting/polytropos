import copy
from typing import Dict, cast

import pytest

from polytropos.actions.changes.available import BestAvailable
from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

t_source: VariableId = cast(VariableId, "t_source")
i_source: VariableId = cast(VariableId, "i_source")
target: VariableId = cast(VariableId, "target")

@pytest.fixture()
def schema() -> Schema:
    t_spec: Dict = {
        "t_source": {
            "name": "t_source",
            "data_type": "Text",
            "sort_order": 0
        }
    }
    temporal: Track = Track.build(t_spec, None, "temporal")
    i_spec: Dict = {
        "i_source": {
            "name": "i_source",
            "data_type": "Text",
            "sort_order": 0
        },
        "target": {
            "name": "target",
            "data_type": "Text",
            "sort_order": 1
        }
    }
    immutable: Track = Track.build(i_spec, None, "immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def composite(schema) -> Composite:
    contents: Dict = {
        "2016": {"t_source": "wrong"},
        "2017": {"t_source": "temporal_expected"},
        "2018": {"t_source": None},
        "2019": {},
        "immutable": {"i_source": "immutable_expected"}
    }
    return Composite(schema, contents)

def test_both_sources_immutable_available(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target, immutable_source=i_source)
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"]["target"] = "immutable_expected"
    change(composite)
    assert composite.content == expected

def test_both_sources_no_temporal_values(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target, immutable_source=i_source)
    del composite.content["2016"]
    del composite.content["2017"]
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"]["target"] = "immutable_expected"
    change(composite)
    assert composite.content == expected

def test_both_sources_immutable_value_missing(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target, immutable_source=i_source)
    del composite.content["immutable"]["i_source"]
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"]["target"] = "temporal_expected"
    change(composite)
    assert composite.content == expected

def test_both_sources_immutable_value_none(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target, immutable_source=i_source)
    composite.content["immutable"]["i_source"] = None
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"]["target"] = "temporal_expected"
    change(composite)
    assert composite.content == expected

def test_both_sources_no_immutable_dict(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target, immutable_source=i_source)
    del composite.content["immutable"]
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"] = {"target": "temporal_expected"}
    change(composite)
    assert composite.content == expected

def test_only_temporal(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target)
    expected: Dict = copy.deepcopy(composite.content)
    expected["immutable"]["target"] = "temporal_expected"
    change(composite)
    assert composite.content == expected

def test_only_temporal_no_valid_values(schema, composite):
    change: Change = BestAvailable(schema, {}, t_source, target)
    del composite.content["2016"]
    del composite.content["2017"]
    expected: Dict = copy.deepcopy(composite.content)
    change(composite)
    assert composite.content == expected
