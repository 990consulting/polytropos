import itertools
from typing import List, Dict, Callable

import pytest

# Just test a couple kinds of primitives to get the point across
from polytropos.ontology.track import Track

types_to_test: List[str] = ["Integer", "Text", "Folder", "List", "NamedList"]

@pytest.fixture
def simple_track() -> Callable:
    def _simple_track(data_type: str) -> Track:
        spec: Dict = {
            "the_var_id": {
                "name": "the_variable",
                "data_type": data_type,
                "sort_order": 0
            }
        }
        track: Track = Track.build(spec, None, "Test")
        return track

    return _simple_track

@pytest.mark.parametrize("original, target", itertools.permutations(types_to_test, 2))
def test_data_type_is_immutable(original, target, simple_track):
    """Any attempt to change the data type of a variable results in an error."""
    track: Track = simple_track(original)
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        track["the_var_id"].data_type = target

@pytest.mark.parametrize("original", types_to_test)
def test_data_type_can_be_read(original, simple_track):
    """Data type can be retrieved as a text property."""
    track: Track = simple_track(original)
    assert track["the_var_id"].data_type == original
