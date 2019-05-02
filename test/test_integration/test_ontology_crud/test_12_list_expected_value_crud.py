"""When checking expected values for lists, one first designates which descendent variables are to be checked. The
expected values themselves consist of the set of observations for a particular instance hierarchy,
where an observation consists of the values for all of the designated descendents. ALL of the designated descendents
must match in order for an observation to match expectations. """

from typing import Dict

import pytest

from etl4.ontology.track import Track

@pytest.fixture()
def list_ev_track() -> Track:
    spec: Dict = {
        "list_without_evs": {
            "name": "A list that has no EVs",
            "data_type": "List",
            "sort_order": 0
        },
        "list_without_evs_field": {
            "name": "A",
            "data_type": "Integer",
            "parent": "list_without_evs",
            "sort_order": 0
        },
        "first_list_with_evs": {
            "name": "First of two lists that have EVs",
            "data_type": "List",
            "sort_order": 1,
            "list_expected_values_fields": [
                "first_list_with_evs_field_1",
                "first_list_with_evs_field_2"
            ],
            "list_expected_values": {
                "case_0": [  # Explicitly expect that case_0 has two observations
                    {
                        "first_list_with_evs_field_1": 17,
                        "first_list_with_evs_field_2": 23
                    },
                    {
                        "first_list_with_evs_field_1": -5,
                        "first_list_with_evs_field_2": None
                    },

                ],
                "case_1": []  # Explicitly expect that case_1 has no observations
            }
        },
        "first_list_with_evs_field_1": {
            "name": "B",
            "data_type": "Integer",
            "parent": "first_list_with_evs",
            "sort_order": 0
        },
        "first_list_with_evs_field_2": {
            "name": "C",
            "data_type": "Integer",
            "parent": "first_list_with_evs",
            "sort_order": 1
        },
        "first_list_with_evs_field_3": {
            "name": "D",
            "data_type": "Integer",
            "parent": "first_list_with_evs",
            "sort_order": 1
        },
        "second_list_with_evs": {
            "name": "Second of two lists that have EVs",
            "data_type": "List",
            "sort_order": 2,
            # List expected value tests check list cardinality, so even without descendents, it's still valuable to list
            # test cases.
            "list_expected_values": {
                "case_1": [
                    {},
                    {},
                ],
                "case_2": []
            }
        },
        "second_list_with_evs_field": {
            "name": "E",
            "data_type": "Integer",
            "parent": "second_list_with_evs",
            "sort_order": 0
        }
    }
    track: Track = Track.build(spec, None, "Test")
    return track

def test_remove_checked_descendent(list_ev_track):
    list_ev_track.set_children_to_test("first_list_with_evs", ["first_list_with_evs_field_1"])
    assert list_ev_track.variables["first_list_with_evs"].dump() == {
        "name": "First of two lists that have EVs",
        "data_type": "List",
        "sort_order": 1,
        "list_expected_values_fields": ["first_list_with_evs_field_1"],
        "list_expected_values": {
            "case_0": [
                {"first_list_with_evs_field_1": 17},
                {"first_list_with_evs_field_1": -5}
            ],
            "case_1": []
        }
    }

def test_remove_all_checked_descendents(list_ev_track):
    """List expected value tests still check list cardinality, so even an empty check is meaningful."""
    list_ev_track.set_children_to_test("first_list_with_evs", [])
    assert list_ev_track.variables["first_list_with_evs"].dump() == {
        "name": "First of two lists that have EVs",
        "data_type": "List",
        "sort_order": 1,
        "list_expected_values_fields": ["first_list_with_evs_field_1"],
        "list_expected_values": {
            "case_0": [
                {},
                {}
            ],
            "case_1": []
        }
    }

def test_add_checked_descendent(list_ev_track):
    list_ev_track.set_children_to_test("first_list_with_evs", [
                "first_list_with_evs_field_1",
                "first_list_with_evs_field_2",
                "first_list_with_evs_field_3"
            ])
    assert list_ev_track.variables["first_list_with_evs"].dump() == {
        "name": "First of two lists that have EVs",
        "data_type": "List",
        "sort_order": 1,
        "list_expected_values_fields": [
            "first_list_with_evs_field_1",
            "first_list_with_evs_field_2"
        ],
        "list_expected_values": {
            "case_0": [  # Explicitly expect that case_0 has two observations
                {
                    "first_list_with_evs_field_1": 17,
                    "first_list_with_evs_field_2": 23,
                    "first_list_with_evs_field_3": None
                },
                {
                    "first_list_with_evs_field_1": -5,
                    "first_list_with_evs_field_2": None,
                    "first_list_with_evs_field_3": None
                }
            ],
            "case_1": []  # Explicitly expect that case_1 has no observations
        }
    }

def test_designate_nonexistent_descendent_raises(list_ev_track):
    with pytest.raises(ValueError):
        list_ev_track.set_children_to_test("first_list_with_evs", ["not a real variable ID"])

def test_add_list_expected_value_affects_var_dict(list_ev_track):
    list_ev_track.set_list_expected_values("list_without_evs", "case_1", [{}, {}, {}])
    assert list_ev_track.variables["list_without_evs"].dump() == {
        "name": "A list that has no EVs",
        "data_type": "List",
        "sort_order": 0,
        "list_expected_values": {
            "case_1": [{}, {}, {}]
        }
    }

def test_add_list_expected_value_with_unexpected_descendent_raises(list_ev_track):
    with pytest.raises(ValueError):
        list_ev_track.set_list_expected_values("list_without_evs", "case_1", [{
            "list_without_evs_field": 72
        }])

def test_remove_list_expected_value_affects_var_dict(list_ev_track):
    list_ev_track.remove_primitive_expected_value("first_list_with_evs", "case_0")
    assert list_ev_track.variables["first_list_with_evs"].dump() == {
        "name": "First of two lists that have EVs",
        "data_type": "List",
        "sort_order": 1,
        "list_expected_values_fields": [
            "first_list_with_evs_field_1",
            "first_list_with_evs_field_2"
        ],
        "list_expected_values": {
            "case_1": []
        }
    }

def test_replace_list_expected_value_affects_var_dict(list_ev_track):
    list_ev_track.set_list_expected_values("first_list_with_evs", "case_0", [])
    assert list_ev_track.variables["first_list_with_evs"].dump() == {
        "name": "First of two lists that have EVs",
        "data_type": "List",
        "sort_order": 1,
        "list_expected_values_fields": [
            "first_list_with_evs_field_1",
            "first_list_with_evs_field_2"
        ],
        "list_expected_values": {
            "case_0": [],
            "case_1": []
        }
    }

def test_add_variable_test_case_affects_track_test_cases(list_ev_track):
    list_ev_track.set_list_expected_values("list_without_evs", "case_3", [{}, {}, {}])
    assert set(list_ev_track.test_cases) == {"case_0", "case_1", "case_2", "case_3"}

def test_remove_variable_test_case_affects_track_test_cases(list_ev_track):
    list_ev_track.remove_primitive_expected_value("first_list_with_evs", "case_0")
    assert set(list_ev_track.test_cases) == {"case_1", "case_2"}

def test_remove_one_of_two_for_case_does_not_affect_track_test_cases(list_ev_track):
    list_ev_track.remove_primitive_expected_value("first_list_with_evs", "case_1")
    assert set(list_ev_track.test_cases) == {"case_0", "case_1", "case_2"}

def test_replace_variable_test_case_does_not_affect_track_test_cases(list_ev_track):
    list_ev_track.set_list_expected_values("first_list_with_evs", "case_0", [])
    assert set(list_ev_track.test_cases) == {"case_0", "case_1", "case_2"}

def test_omitting_expected_values_for_designated_list_descendents_raises(list_ev_track):
    with pytest.raises(ValueError):
        list_ev_track.set_list_expected_values("first_list_with_evs", "case_0", [
            {
                "first_list_with_evs_field_1": 17
            }
        ])
