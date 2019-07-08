from typing import Dict

import pytest

from polytropos.ontology.track import Track

@pytest.fixture()
def has_all_track() -> Track:
    spec: Dict = {
        "the_var_id": {
            "name": "var with all metadata",
            "data_type": "Integer",
            "sort_order": 0,
            "notes": "This is a note that I left for myself about this variable.",
            "earliest_epoch": "2011",
            "latest_epoch": "2019-01-02"
        }
    }
    track: Track = Track.build(spec, None, "Test")
    return track

@pytest.fixture()
def has_none_track() -> Track:
    spec: Dict = {
        "the_var_id": {
            "name": "var with no metadata",
            "data_type": "Integer",
            "sort_order": 0
        }
    }
    track: Track = Track.build(spec, None, "Test")
    return track

def test_add_metadata_field(has_none_track):
    has_none_track["the_var_id"].notes = "This is a note"
    assert has_none_track["the_var_id"].dump() == {
        "name": "var with no metadata",
        "data_type": "Integer",
        "sort_order": 0,
        "notes": "This is a note"
    }

@pytest.mark.parametrize("value", [
    "A new note",
    " A new note",
    " A new note ",
    "\nA new note ",
    "\tA new note\r\n ",
])
def test_alter_metadata_field(has_all_track, value):
    """Leading and trailing whitespace should be ignored, as these values will be coming from a web form"""
    has_all_track["the_var_id"].notes = value
    assert has_all_track["the_var_id"].dump() == {
        "name": "var with all metadata",
        "data_type": "Integer",
        "sort_order": 0,
        "notes": "A new note",
        "earliest_epoch": "2011",
        "latest_epoch": "2019-01-02"
    }

def test_clear_metadata_field(has_all_track):
    has_all_track["the_var_id"].notes = None
    assert has_all_track["the_var_id"].dump() == {
        "name": "var with all metadata",
        "data_type": "Integer",
        "sort_order": 0,
        "earliest_epoch": "2011",
        "latest_epoch": "2019-01-02"
    }


@pytest.mark.parametrize("value", ["", " ", "  ", "\n", "\t", "\r\n"])
def test_empty_string_same_as_none(has_all_track, value):
    has_all_track["the_var_id"].notes = value
    assert has_all_track["the_var_id"].dump() == {
        "name": "var with all metadata",
        "data_type": "Integer",
        "sort_order": 0,
        "earliest_epoch": "2011",
        "latest_epoch": "2019-01-02"
    }

# TODO Quimey, I only tested one field, but please let me know if you are able to achieve a solution as described above.
#  IF not, I will add more tests here.
