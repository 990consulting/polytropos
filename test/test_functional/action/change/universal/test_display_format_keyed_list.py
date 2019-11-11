import copy
from collections import Callable
from typing import Dict, cast, List, Tuple

import pytest

from polytropos.actions.changes.display import DisplayFormat
from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def make_schema(make_spec) -> Callable:
    # noinspection DuplicatedCode
    def _make_schema(temporal: bool) -> Schema:
        spec: Dict = make_spec()
        spec["containing_keyed_list"] = {
            "name": "the_keyed_list",
            "data_type": "KeyedList",
            "sort_order": 0
        }
        spec["source"]["parent"] = "containing_keyed_list"

        if temporal:
            temporal: Track = Track.build(spec, None, "temporal")
            immutable: Track = Track.build({}, None, "immutable")
            schema: Schema = Schema(temporal, immutable)
        else:
            immutable: Track = Track.build(spec, None, "immutable")
            temporal: Track = Track.build({}, None, "temporal")
            schema: Schema = Schema(temporal, immutable)

        return schema
    return _make_schema

@pytest.fixture()
def do_test() -> Callable:
    # noinspection DuplicatedCode
    def _do_test(schema: Schema, content: Dict, expected: Dict) -> None:
        composite: Composite = Composite(schema, content)
        folder: VariableId = cast(VariableId, "source")
        target: VariableId = cast(VariableId, "target")
        list_base: VariableId = cast(VariableId, "containing_keyed_list")
        change: Change = DisplayFormat(schema, {}, folder, target, list_base=list_base)
        change(composite)
        assert content == expected
    return _do_test

@pytest.fixture()
def observation() -> Dict:
    return {
        "the_keyed_list": {
            "red": {"phone": "5088675309"},
            "blue": {"phone": "1-800-DRUIDIA"},
            "black": {"phone": None},
            "green": {},
        }
    }

regimes: List[Tuple[bool, str]] = [
    (False, "immutable"),
    (True, "temporal")
]

@pytest.mark.parametrize("temporal, period", regimes)
def test_checkbox_list(make_schema, observation, do_test, temporal, period):
    schema: Schema = make_schema(temporal)
    content: Dict = {period: observation}
    expected: Dict = copy.deepcopy(content)
    expected[period]["the_keyed_list"]["red"]["the_target"] = "+1 (508) 867-5309"
    expected[period]["the_keyed_list"]["blue"]["the_target"] = "1-800-DRUIDIA"
    do_test(schema, content, expected)
