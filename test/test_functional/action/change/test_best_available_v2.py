import copy
from typing import Dict, cast

import pytest

from polytropos.actions.changes.available_v2 import BestAvailableV2
from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

t_source_1: VariableId = cast(VariableId, "t_source_1")
t_source_2: VariableId = cast(VariableId, "t_source_2")
t_source_3: VariableId = cast(VariableId, "t_source_3")
i_source_1: VariableId = cast(VariableId, "i_source_1")
i_source_2: VariableId = cast(VariableId, "i_source_2")
i_source_3: VariableId = cast(VariableId, "i_source_3")
target: VariableId = cast(VariableId, "target")


@pytest.fixture()
def schema() -> Schema:
    t_spec: Dict = {
        "t_source_1": {
            "name": "t_source_1",
            "data_type": "Text",
            "sort_order": 0
        },
        "t_source_2": {
            "name": "t_source_2",
            "data_type": "Text",
            "sort_order": 0
        },
        "t_source_3": {
            "name": "t_source_3",
            "data_type": "Integer",
            "sort_order": 0
        },
    }
    temporal: Track = Track.build(t_spec, None, "temporal")
    i_spec: Dict = {
        "i_source_1": {
            "name": "i_source_1",
            "data_type": "Text",
            "sort_order": 0
        },
        "i_source_2": {
            "name": "i_source_2",
            "data_type": "Text",
            "sort_order": 0
        },
        "i_source_3": {
            "name": "i_source_3",
            "data_type": "Currency",
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
        "2016": {"t_source_1": "temporal_2016_1", "t_source_2": "temporal_2016_2"},
        "2017": {"t_source_1": "temporal_2017_1", "t_source_2": "temporal_2017_2"},
        "2018": {"t_source_1": None, "t_source_2": "temporal_2018_2"},
        "2019": {"t_source_2": "temporal_2019_2"},
        "immutable": {"i_source_1": "immutable_1"}
    }
    return Composite(schema, contents)


def test_no_sources(schema, composite):
    change: Change = BestAvailableV2(schema, {}, target, [])
    expected: Dict = copy.deepcopy(composite.content)
    change(composite)
    assert composite.content == expected


@pytest.mark.parametrize("sources", [
    ([i_source_3]),
    ([i_source_3, t_source_1]),
    ([t_source_2, i_source_3]),
    ([t_source_3]),
    ([i_source_2, t_source_3]),
    ([i_source_1, t_source_2, t_source_3, i_source_1]),
])
def test_sources_with_different_data_types(schema, composite, sources):
    with pytest.raises(ValueError):
        change: Change = BestAvailableV2(schema, {}, target, sources)


@pytest.mark.parametrize("sources, expected_target", [
    ([i_source_1], "immutable_1"),
    ([i_source_2], None),
    ([t_source_1], "temporal_2017_1"),
    ([t_source_2], "temporal_2019_2"),
    ([i_source_2, i_source_1], "immutable_1"),
    ([i_source_2, t_source_2], "temporal_2019_2"),
    ([t_source_1, t_source_2], "temporal_2017_1"),
    ([i_source_1, t_source_1], "immutable_1"),
    ([i_source_2, t_source_2, i_source_1], "temporal_2019_2"),
    ([i_source_2, i_source_1, t_source_2], "immutable_1"),
])
def test_sources(schema, composite, sources, expected_target):
    change: Change = BestAvailableV2(schema, {}, target, sources)
    expected: Dict = copy.deepcopy(composite.content)
    if expected_target is not None:
        expected["immutable"]["target"] = expected_target
    change(composite)
    assert composite.content == expected


@pytest.mark.parametrize("sources, expected_target", [
    ([i_source_1], "immutable_1"),
    ([i_source_2], None),
    ([t_source_1], None),
    ([t_source_2], "temporal_2019_2"),
    ([i_source_2, i_source_1], "immutable_1"),
    ([i_source_2, t_source_1], None),
    ([t_source_1, t_source_2], "temporal_2019_2"),
    ([i_source_1, t_source_1], "immutable_1"),
    ([i_source_2, t_source_1, i_source_1], "immutable_1"),
    ([i_source_2, t_source_1, t_source_2], "temporal_2019_2"),
])
def test_sources_use_only_current(schema, composite, sources, expected_target):
    change: Change = BestAvailableV2(schema, {}, target, sources, use_only_current=True)
    expected: Dict = copy.deepcopy(composite.content)
    if expected_target is not None:
        expected["immutable"]["target"] = expected_target
    change(composite)
    assert composite.content == expected


@pytest.mark.parametrize("sources, expected_target", [
    ([i_source_1], "immutable_1"),
    ([i_source_2], None),
    ([t_source_1], None),
    ([t_source_2], None),
    ([i_source_2, i_source_1], "immutable_1"),
    ([i_source_2, t_source_2], None),
    ([t_source_1, t_source_2], None),
    ([i_source_1, t_source_1], "immutable_1"),
    ([i_source_2, t_source_2, i_source_1], "immutable_1"),
    ([i_source_2, i_source_1, t_source_2], "immutable_1"),
])
def test_sources_no_temporal_values(schema, composite, sources, expected_target):
    change: Change = BestAvailableV2(schema, {}, target, sources)
    del composite.content["2016"]
    del composite.content["2017"]
    del composite.content["2018"]
    del composite.content["2019"]
    expected: Dict = copy.deepcopy(composite.content)
    if expected_target is not None:
        expected["immutable"]["target"] = expected_target
    change(composite)
    assert composite.content == expected


@pytest.mark.parametrize("sources, expected_target", [
    ([i_source_1], "immutable_1"),
    ([i_source_2], None),
    ([t_source_1], None),
    ([t_source_2], None),
    ([i_source_2, i_source_1], "immutable_1"),
    ([i_source_2, t_source_1], None),
    ([t_source_1, t_source_2], None),
    ([i_source_1, t_source_1], "immutable_1"),
    ([i_source_2, t_source_1, i_source_1], "immutable_1"),
    ([i_source_2, t_source_1, t_source_2], None),
])
def test_sources_no_temporal_values_use_only_current(schema, composite, sources, expected_target):
    change: Change = BestAvailableV2(schema, {}, target, sources, use_only_current=True)
    del composite.content["2016"]
    del composite.content["2017"]
    del composite.content["2018"]
    del composite.content["2019"]
    expected: Dict = copy.deepcopy(composite.content)
    if expected_target is not None:
        expected["immutable"]["target"] = expected_target
    change(composite)
    assert composite.content == expected


@pytest.mark.parametrize("sources, expected_target", [
    ([i_source_1], None),
    ([i_source_2], None),
    ([t_source_1], "temporal_2017_1"),
    ([t_source_2], "temporal_2019_2"),
    ([i_source_2, i_source_1], None),
    ([i_source_2, t_source_2], "temporal_2019_2"),
    ([t_source_1, t_source_2], "temporal_2017_1"),
    ([i_source_1, t_source_1], "temporal_2017_1"),
    ([i_source_2, t_source_2, i_source_1], "temporal_2019_2"),
    ([i_source_2, i_source_1, t_source_2], "temporal_2019_2"),
])
def test_sources_no_immutable_values(schema, composite, sources, expected_target):
    change: Change = BestAvailableV2(schema, {}, target, sources)
    del composite.content["immutable"]
    expected: Dict = copy.deepcopy(composite.content)
    if expected_target is not None:
        expected.setdefault("immutable", {})["target"] = expected_target
    change(composite)
    assert composite.content == expected


@pytest.mark.parametrize("sources, expected_target", [
    ([i_source_1], None),
    ([i_source_2], None),
    ([t_source_1], None),
    ([t_source_2], "temporal_2019_2"),
    ([i_source_2, i_source_1], None),
    ([i_source_2, t_source_1], None),
    ([t_source_1, t_source_2], "temporal_2019_2"),
    ([i_source_1, t_source_1], None),
    ([i_source_2, t_source_1, i_source_1], None),
    ([i_source_2, t_source_1, t_source_2], "temporal_2019_2"),
])
def test_sources_no_immutable_values_use_only_current(schema, composite, sources, expected_target):
    change: Change = BestAvailableV2(schema, {}, target, sources, use_only_current=True)
    del composite.content["immutable"]
    expected: Dict = copy.deepcopy(composite.content)
    if expected_target is not None:
        expected.setdefault("immutable", {})["target"] = expected_target
    change(composite)
    assert composite.content == expected
