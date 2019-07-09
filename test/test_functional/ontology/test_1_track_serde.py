"""Verify basic serialization/deserialization behavior for variables and tracks. Does not fully exericse all of the
optional fields; these are tested in downstream integration tests. Variable-level validation is also tested in
downstream tests."""

from typing import Dict
import pytest
from polytropos.ontology.track import Track
import sys
import inspect


def test_dump(simple_track, simple_spec):
    """Convert the source spec dict to a track, then back to a dict"""
    actual: Dict = simple_track.dump()
    assert simple_spec == actual

def test_dumps_pretty(simple_spec):
    """Verify that, regardless of how the input dict was formatted, dumps is pretty and alphabetized by variable ID."""

    # Dictionary insertion order is preserved (as a language feature) from Python 3.7 onward
    assert sys.version_info >= (3, 7), "This module requires Python 3.7+"

    out_of_order_spec: Dict = {
        "target_var_id": simple_spec["target_var_id"],
        "target_folder": simple_spec["target_folder"]
    }

    track: Track = Track.build(out_of_order_spec, None, "OOO")
    actual: str = track.dumps()
    expected: str = inspect.cleandoc("""
    {
      "target_folder": {
        "name": "the_folder",
        "data_type": "Folder",
        "sort_order": 0
      },
      "target_var_id": {
        "name": "the_target",
        "data_type": "Integer",
        "sort_order": 0,
        "parent": "target_folder"
      }
    }""")
    assert actual == expected
