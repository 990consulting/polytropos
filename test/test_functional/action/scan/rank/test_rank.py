import json
import os
import shutil
import tempfile
from typing import Dict, cast, Callable

from polytropos.util.paths import relpath_for

from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema

from polytropos.actions.scan.rank import Rank
import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

base_path: str = os.path.dirname(os.path.abspath(__file__))

target: VariableId = cast(VariableId, "the_target")

@pytest.fixture(scope="module")
def schema() -> Schema:
    spec: Dict = {
        "integer_source": {
            "name": "integer_source",
            "data_type": "Integer",
            "sort_order": 0
        },
        "currency_source": {
            "name": "currency_source",
            "data_type": "Currency",
            "sort_order": 1
        },
        "decimal_source": {
            "name": "decimal_source",
            "data_type": "Decimal",
            "sort_order": 2
        },
        "the_target": {
            "name": "rank",
            "data_type": "Integer",
            "sort_order": 3
        }
    }
    immutable: Track = Track.build(spec, None, "immutable")
    temporal: Track = Track.build({}, None, "temporal")
    return Schema(temporal, immutable)

@pytest.fixture()
def setup_teardown(schema):
    working_path: str = tempfile.mkdtemp()
    input_dir: str = os.path.join(working_path, "input")
    actual_dir: str = os.path.join(working_path, "output")
    shutil.copytree(os.path.join(base_path, "input"), input_dir)
    yield input_dir, actual_dir
    shutil.rmtree(working_path)

@pytest.mark.parametrize("source_type", ["integer", "currency", "decimal"])
def test_rank(setup_teardown, schema, source_type) -> None:
    source: VariableId = cast(VariableId, "{}_source".format(source_type))
    input_dir, actual_dir = setup_teardown
    with Context("", "", "", "", "", "", "", False, 1, False, True) as context:
        rank: Rank = Rank(context, schema, source, target)
        rank(input_dir, actual_dir)
    for index in range(1, 6):
        composite_id: str = "{:09}".format(index)
        relpath: str = relpath_for(composite_id)
        e_path: str = os.path.join(base_path, "expected", relpath, "%s.json" % composite_id)
        a_path: str = os.path.join(actual_dir, relpath, "%s.json" % composite_id)
        with open(e_path) as e_fh, open(a_path) as a_fh:
            expected: Dict = json.load(e_fh)
            actual: Dict = json.load(a_fh)
        assert actual == expected