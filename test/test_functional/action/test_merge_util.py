import os
from typing import Dict
import json
from polytropos.actions.merge.util import merge_dicts
import pytest

@pytest.mark.parametrize("filename", ["composite_3.json", "composite_4.json"])
def test_merge_dicts(filename: str, basepath: str) -> None:
    rel_path: str = "com/pos/ite/{}".format(filename)
    fixture_base: str = os.path.join(basepath, "..", "examples", "s_10_merge", "data", "entities")
    primary_fn: str = os.path.join(fixture_base, "p", rel_path)
    secondary_fn: str = os.path.join(fixture_base, "q", rel_path)
    expected_fn: str = os.path.join(fixture_base, "expected", rel_path)

    with open(primary_fn) as primary_fh, open(secondary_fn) as secondary_fh, open(expected_fn) as expected_fh:
        primary: Dict = json.load(primary_fh)
        secondary: Dict = json.load(secondary_fh)
        expected: Dict = json.load(expected_fh)

    actual: Dict = merge_dicts(primary, secondary)
    assert actual == expected