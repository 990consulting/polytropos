"""
The tests check if a cache will be cleaned after updating the "parent" property of the variables.

The `variable.parent` can be changed using `duplicate`, `add`, `delete`, `move` methods of a track
instance as well as using direct modification of variables using `track[var_id].parent`.
"""
from typing import Iterator

from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable


def _validate_roots(
    actual_roots: Iterator[Variable], number_of_roots: int
):
    result = list(actual_roots)
    assert len(result) == number_of_roots


def test_duplicate():
    track = Track.build(
        {
            "a": {"name": "a", "data_type": "Folder", "parent": "", "sort_order": 0},
            "b": {"name": "b", "data_type": "Variable", "parent": "a", "sort_order": 0},
        },
        None,
        "duplicate",
    )
    _validate_roots(track.roots, 1)
    track.duplicate("a", "c")
    _validate_roots(track.roots, 2)


def test_add():
    track = Track.build(
        {
            "a": {"name": "a", "data_type": "Folder", "parent": "", "sort_order": 0},
            "b": {"name": "b", "data_type": "Variable", "parent": "a", "sort_order": 0},
        },
        None,
        "duplicate",
    )
    _validate_roots(track.roots, 1)
    track.add({"name": "c", "data_type": "List", "parent": "", "sort_order": 0}, "c")
    _validate_roots(track.roots, 2)


def test_delete():
    track = Track.build(
        {
            "a": {"name": "a", "data_type": "Folder", "parent": "", "sort_order": 0},
            "b": {"name": "b", "data_type": "Variable", "parent": "a", "sort_order": 0},
            "c": {"name": "c", "data_type": "List", "parent": "", "sort_order": 0},
        },
        None,
        "duplicate",
    )
    _validate_roots(track.roots, 2)
    track.delete("c")
    _validate_roots(track.roots, 1)


def test_move():
    track = Track.build(
        {
            "a": {"name": "a", "data_type": "Folder", "parent": "", "sort_order": 0},
            "b": {"name": "b", "data_type": "Variable", "parent": "a", "sort_order": 0},
        },
        None,
        "duplicate",
    )
    _validate_roots(track.roots, 1)
    track.move("b", None, 0)
    _validate_roots(track.roots, 2)


def test_direct_manipulation():
    track = Track.build(
        {
            "a": {"name": "a", "data_type": "Folder", "parent": "", "sort_order": 0},
            "b": {"name": "b", "data_type": "Variable", "parent": "a", "sort_order": 0},
        },
        None,
        "duplicate",
    )
    _validate_roots(track.roots, 1)
    track["b"].parent = ""
    _validate_roots(track.roots, 2)
