import json
from typing import Dict, List
import os

import pytest

from polytropos.tools.schema.uispec import GUITreeToSpec

base_path: str = os.path.dirname(os.path.realpath(__file__))

input_path: str = os.path.join(base_path, "from_gui.json")
with open(input_path) as fh:
    input_spec: List[Dict] = json.load(fh)

expected_path: str = os.path.join(base_path, "expected.json")
with open(expected_path) as fh:
    expected_spec: Dict = json.load(fh)

convert: GUITreeToSpec = GUITreeToSpec(input_spec)
output_spec: Dict = convert()

def test_keys_match():
    assert output_spec.keys() == expected_spec.keys()

@pytest.mark.parametrize("key", expected_spec.keys())
def test_content_matches(key: str):
    if key not in output_spec:
        pytest.fail()

    assert output_spec[key] == expected_spec[key]
