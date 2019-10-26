import json
import os
import shutil
import tempfile
from typing import Dict, cast
from unittest.mock import MagicMock

from polytropos.util.paths import relpath_for

from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema

from polytropos.actions.scan.quantile import Quantile
import pytest

from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

base_path: str = os.path.dirname(os.path.abspath(__file__))
working_path: str = tempfile.mkdtemp()
input_dir: str = os.path.join(working_path, "input")
actual_dir: str = os.path.join(working_path, "output")

source: VariableId = cast(VariableId, "the_source")
target: VariableId = cast(VariableId, "the_target")

@pytest.fixture(scope="module")
def schema() -> Schema:
    spec: Dict = {
        "the_source": {
            "name": "source",
            "data_type": "Integer",
            "sort_order": 0
        },
        "the_target": {
            "name": "quantile",
            "data_type": "Decimal",
            "sort_order": 1
        }
    }
    immutable: Track = Track.build(spec, None, "immutable")
    temporal: Track = Track.build({}, None, "temporal")
    return Schema(temporal, immutable)

@pytest.fixture(scope="module", autouse=True)
def setup_teardown(schema):
    shutil.copytree(os.path.join(base_path, "input"), input_dir)
    with Context("", "", "", "", "", "", "", False, 1, False, True) as context:
        quantile: Quantile = Quantile(context, schema, source, target)
        quantile(input_dir, actual_dir)
    yield
    shutil.rmtree(working_path)

@pytest.mark.parametrize("index", range(1, 6))
def test_quantile_outcome(index: int):
    composite_id: str = "{:09}".format(index)
    relpath: str = relpath_for(composite_id)
    e_path: str = os.path.join(base_path, "expected", relpath, "%s.json" % composite_id)
    a_path: str = os.path.join(working_path, "output", relpath, "%s.json" % composite_id)
    with open(e_path) as e_fh, open(a_path) as a_fh:
        expected: Dict = json.load(e_fh)
        actual: Dict = json.load(a_fh)
    assert actual == expected
