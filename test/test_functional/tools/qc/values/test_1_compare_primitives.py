import pytest
from typing import Optional, Any
from polytropos.tools.qc.values import compare_primitives

@pytest.mark.parametrize("fixture, actual, expected", [
    (None, None, True),
    (0, 0.0, True),
    (-1.0, -1, True),
    (0.001, 0.001000, True),
    ("A", "A", True),
    (True, True, True),
    (False, False, True),
    ("A", "a", False),
    (None, 0, False),
    (None, 0.0, False),
    (None, 0.1, False),
    (None, True, False),
    (None, False, False),
    ("a", None, False),
    (0, None, False)
])
def test_compare_primitives(fixture: Optional[Any], actual: Optional[Any], expected: bool):
    observed: bool = compare_primitives(fixture, actual)
    assert observed == expected