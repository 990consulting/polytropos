from typing import Dict

import pytest

from polytropos.ontology.track import Track

@pytest.fixture()
def simple_ev_track() -> Track:
    spec: Dict = {
        "with_ev": {
            "name": "var_with_ev",
            "data_type": "Text",
            "sort_order": 0,
            "simple_expected_values": {
                "case_0": "ABC",
                "case_1": "CDE"
            }
        },
        "without_ev": {
            "name": "var_without_ev",
            "data_type": "Text",
            "sort_order": 1
        },
        "another_with_ev": {
            "name": "some_other_var",
            "data_type": "Text",
            "sort_order": 2,
            "simple_expected_values": {
                "case_1": "AAA"
            }
        }
    }
    return Track.build(spec, None, "Test")

def test_add_simple_expected_value_affects_var_dict(simple_ev_track):
    simple_ev_track.set_primitive_expected_value("without_ev", "the_instance", "the_value")
    assert simple_ev_track["without_ev"].dump() == {
        "name": "var_without_ev",
        "data_type": "Text",
        "sort_order": 1,
        "simple_expected_values": {
            "the_instance": "the_value"
        }
    }

def test_remove_simple_expected_value_affects_var_dict(simple_ev_track):
    simple_ev_track.remove_primitive_expected_value("with_ev", "case_0")
    assert simple_ev_track["with_ev"].dump() == {
        "name": "var_with_ev",
        "data_type": "Text",
        "sort_order": 0,
        "simple_expected_values": {
            "case_1": "CDE"
        }
    }

def test_replace_simple_expected_value_affects_var_dict(simple_ev_track):
    simple_ev_track.set_primitive_expected_value("with_ev", "case_0", "XYZ")
    assert simple_ev_track["with_ev"].dump() == {
        "name": "var_with_ev",
        "data_type": "Text",
        "sort_order": 0,
        "simple_expected_values": {
            "case_0": "XYZ",
            "case_1": "CDE"
        }
    }

def test_add_simple_expected_value_affects_track_test_cases(simple_ev_track):
    simple_ev_track.set_primitive_expected_value("without_ev", "the_instance", "the_value")
    assert set(simple_ev_track.test_cases) == {"case_0", "case_1", "the_instance"}

def test_remove_simple_expected_value_affects_track_test_cases(simple_ev_track):
    simple_ev_track.remove_primitive_expected_value("with_ev", "case_0")
    assert set(simple_ev_track.test_cases) == {"case_1"}

def test_add_simple_expected_value_where_already_exists(simple_ev_track):
    simple_ev_track.set_primitive_expected_value("without_ev", "case_1", "the_value")
    assert set(simple_ev_track.test_cases) == {"case_0", "case_1"}

def test_remove_simple_expected_value_where_two_exist(simple_ev_track):
    simple_ev_track.remove_primitive_expected_value("another_with_ev", "case_1")
    assert set(simple_ev_track.test_cases) == {"case_0", "case_1"}

def test_replace_simple_expected_value_does_not_affect_track_test_cases(simple_ev_track):
    simple_ev_track.set_primitive_expected_value("with_ev", "case_0", "XYZ")
    assert set(simple_ev_track.test_cases) == {"case_0", "case_1"}

