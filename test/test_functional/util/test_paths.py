import os
from typing import Set

import pytest

from polytropos.util.paths import find_all_composites, relpath_for

def test_find_all_composites(basepath):
    fixture_basepath: str = os.path.join(basepath, "test_functional", "util", "path_fixtures")
    expected: Set[str] = {"02164", "380476abcxyz", "person_3"}
    actual: Set[str] = set(find_all_composites(fixture_basepath))
    assert actual == expected

@pytest.mark.parametrize("composite_id, expected", [
    ("02164", "021"),
    ("380476abcxyz", "380/476/abc"),
    ("person_3", "per/son")
])
def test_relpath_for(composite_id: str, expected: str):
    assert relpath_for(composite_id) == expected
