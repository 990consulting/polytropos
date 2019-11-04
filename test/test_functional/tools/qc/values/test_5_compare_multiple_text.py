import pytest
from typing import Optional, Any
from polytropos.tools.qc.values import compare_multiple_text


@pytest.mark.parametrize("fixture, actual, expected", [
    ([], None, False),
    (["a"], [], False),
    ([], ["a"], False),
    (["a"], ["a"], True),
    (["a", "b"], ["a"], False),
    (["b"], ["a", "b"], False),
    (["b", "a"], ["a", "b"], False),
    (["a", "b"], ["a", "b"], True),
])
def test_compare_multiple_text(fixture: Optional[Any], actual: Optional[Any], expected: bool):
    observed: bool = compare_multiple_text(fixture, actual)
    assert observed == expected
