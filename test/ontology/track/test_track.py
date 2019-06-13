from typing import Iterator

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable


def _validate_roots(
    actual_roots: Iterator[Variable], number_of_roots: int, expected_root: Variable
):
    result = list(actual_roots)
    assert len(result) == number_of_roots
    assert all(expected_root == root for root in result)


def test_roots_memoization_with_cache_invalidation():
    expected_variable = Variable("a", 0)
    track = Track(
        {"a": expected_variable, "b": Variable("b", 1, parent="pb")}, None, "test"
    )
    _validate_roots(track.roots, 1, expected_variable)
    track.duplicate("a", "c")
    _validate_roots(track.roots, 2, expected_variable)
