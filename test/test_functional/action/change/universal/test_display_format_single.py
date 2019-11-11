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
    def _make_schema(temporal: bool) -> Schema:
        if temporal:
            temporal: Track = Track.build(make_spec(), None, "temporal")
            immutable: Track = Track.build({}, None, "immutable")
            schema: Schema = Schema(temporal, immutable)
        else:
            immutable: Track = Track.build(make_spec(), None, "immutable")
            temporal: Track = Track.build({}, None, "temporal")
            schema: Schema = Schema(temporal, immutable)

        return schema
    return _make_schema

@pytest.fixture()
def do_test() -> Callable:
    def _do_test(schema: Schema, content: Dict, expected: Dict) -> None:
        composite: Composite = Composite(schema, content)
        source: VariableId = cast(VariableId, "source")
        target: VariableId = cast(VariableId, "target")
        change: Change = DisplayFormat(schema, {}, source, target)
        change(composite)
        assert content == expected
    return _do_test


@pytest.fixture()
def observation() -> Dict:
    return {
        "phone": "5088675309"
    }

regimes: List[Tuple[bool, str]] = [
    (False, "immutable"),
    (True, "temporal")
]

@pytest.mark.parametrize("temporal, period", regimes)
def test_single(make_schema, observation, do_test, temporal, period):
    schema: Schema = make_schema(temporal)
    content: Dict = {period: observation}
    expected: Dict = copy.deepcopy(content)
    expected[period]["the_target"] = "+1 (508) 867-5309"
    do_test(schema, content, expected)
