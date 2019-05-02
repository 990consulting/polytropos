from typing import Dict

import pytest

from etl4.ontology.track import Track

@pytest.fixture()
def named_list_ev_track() -> Track:
    spec: Dict = {
        "named_list_without_evs": {
            "name": "A named list that has no EVs",
            "data_type": "NamedList",
            "sort_order": 0
        },
        "named_list_without_evs_field": {
            "name": "A",
            "data_type": "Integer",
            "parent": "named_list_without_evs",
            "sort_order": 0
        },
        "first_named_list_with_evs": {
            "name": "First of two named lists that have EVs",
            "data_type": "NamedList",
            "sort_order": 1,
            "list_expected_values_fields": [  # Note that both lists and named lists use this same property
                "first_named_list_with_evs_field_1",
                "first_named_list_with_evs_field_2"
            ],
            "named_list_expected_values": {
                "case_0": {
                    "steve": {
                        "first_named_list_with_evs_field_1": 17,
                        "first_named_list_with_evs_field_2": 23
                    },
                    "mary": {
                        "first_named_list_with_evs_field_1": -5,
                        "first_named_list_with_evs_field_2": None
                    }
                },
                "case_1": {}
            }
        },
        "first_named_list_with_evs_field_1": {
            "name": "B",
            "data_type": "Integer",
            "parent": "first_named_list_with_evs",
            "sort_order": 0
        },
        "first_named_list_with_evs_field_2": {
            "name": "C",
            "data_type": "Integer",
            "parent": "first_named_list_with_evs",
            "sort_order": 1
        },
        "first_named_list_with_evs_field_3": {
            "name": "D",
            "data_type": "Integer",
            "parent": "first_named_list_with_evs",
            "sort_order": 1
        },
        "second_named_list_with_evs": {
            "name": "Second of two named lists that have EVs",
            "data_type": "NamedList",
            "sort_order": 2,
            "named_list_expected_values": {
                "case_1": {
                    "steve": {},
                    "mary": {},
                },
                "case_2": {}
            }
        },
        "second_named_list_with_evs_field": {
            "name": "E",
            "data_type": "Integer",
            "parent": "second_named_list_with_evs",
            "sort_order": 0
        }
    }
    track: Track = Track.build(spec, None, "Test")
    return track

def test_remove_checked_descendent(named_list_ev_track):
    named_list_ev_track.set_children_to_test("first_named_list_with_evs", ["first_named_list_with_evs_field_1"])
    assert named_list_ev_track.variables["first_named_list_with_evs"].dump() == {
        "name": "First of two named lists that have EVs",
        "data_type": "NamedList",
        "sort_order": 1,
        "list_expected_values_fields": ["first_named_list_with_evs_field_1"],
        "named_list_expected_values": {
            "case_0": {
                "steve": {"first_named_list_with_evs_field_1": 17},
                "mary": {"first_named_list_with_evs_field_1": -5}
            },
            "case_1": {}
        }
    }

def test_remove_all_checked_descendents(named_list_ev_track):
    named_list_ev_track.set_children_to_test("first_named_list_with_evs", {})
    assert named_list_ev_track.variables["first_named_list_with_evs"].dump() == {
        "name": "First of two named lists that have EVs",
        "data_type": "NamedList",
        "sort_order": 1,
        "named_list_expected_values": {
            "case_0": {
                "steve": {},
                "mary": {}
            },
            "case_1": {}
        }
    }

def test_add_checked_descendent(named_list_ev_track):
    named_list_ev_track.set_children_to_test("first_named_list_with_evs", [
        "first_named_list_with_evs_field_1",
        "first_named_list_with_evs_field_2",
        "first_named_list_with_evs_field_3"
    ])
    assert named_list_ev_track.variables["first_named_list_with_evs"].dump() == {
        "name": "First of two named lists that have EVs",
        "data_type": "NamedList",
        "sort_order": 1,
        "list_expected_values_fields": [
            "first_named_list_with_evs_field_1",
            "first_named_list_with_evs_field_2",
            "first_named_list_with_evs_field_3"
        ],
        "named_list_expected_values": {
            "case_0": {
                "steve": {
                    "first_named_list_with_evs_field_1": 17,
                    "first_named_list_with_evs_field_2": 23,
                    "first_named_list_with_evs_field_3": None
                },
                "mary": {
                    "first_named_list_with_evs_field_1": -5,
                    "first_named_list_with_evs_field_2": None,
                    "first_named_list_with_evs_field_3": None
                }
            },
            "case_1": {}
        }
    }

def test_designate_nonexistent_descendent_raises(named_list_ev_track):
    with pytest.raises(ValueError):
        named_list_ev_track.set_children_to_test("first_named_list_with_evs", ["not a real variable ID"])

def test_add_list_expected_value_affects_var_dict(named_list_ev_track):
    named_list_ev_track.set_named_list_expected_values("named_list_without_evs", "case_1", {
        "steve": {},
        "mary": {},
        "conor": {}
    })
    assert named_list_ev_track.variables["named_list_without_evs"].dump() == {
        "name": "A named list that has no EVs",
        "data_type": "NamedList",
        "sort_order": 0,
        "named_list_expected_values": {
            "case_1": {
                "steve": {},
                "mary": {},
                "conor": {}

            }
        }
    }

def test_add_list_expected_value_with_unexpected_descendent_raises(named_list_ev_track):
    with pytest.raises(ValueError):
        named_list_ev_track.set_named_list_expected_values("named_list_without_evs", "case_1", {
            "steve": {"named_list_without_evs_field": 72}
        })

def test_remove_list_expected_value_affects_var_dict(named_list_ev_track):
    named_list_ev_track.remove_primitive_expected_value("first_named_list_with_evs", "case_0")
    assert named_list_ev_track.variables["first_named_list_with_evs"].dump() == {
        "name": "First of two named lists that have EVs",
        "data_type": "NamedList",
        "sort_order": 1,
        "list_expected_values_fields": [
            "first_named_list_with_evs_field_1",
            "first_named_list_with_evs_field_2"
        ],
        "named_list_expected_values": {
            "case_1": {}
        }
    }

def test_replace_list_expected_value_affects_var_dict(named_list_ev_track):
    named_list_ev_track.set_named_list_expected_values("first_named_list_with_evs", "case_0", {})
    assert named_list_ev_track.variables["first_named_list_with_evs"].dump() == {
        "name": "First of two named lists that have EVs",
        "data_type": "NamedList",
        "sort_order": 1,
        "list_expected_values_fields": [
            "first_named_list_with_evs_field_1",
            "first_named_list_with_evs_field_2"
        ],
        "named_list_expected_values": {
            "case_0": {},
            "case_1": {}
        }
    }

def test_add_variable_test_case_affects_track_test_cases(named_list_ev_track):
    named_list_ev_track.set_named_list_expected_values("named_list_without_evs", "case_3", {
        "steve": {},
        "mary": {},
        "conor": {}
    })
    assert set(named_list_ev_track.test_cases) == {"case_0", "case_1", "case_2", "case_3"}

def test_remove_variable_test_case_affects_track_test_cases(named_list_ev_track):
    named_list_ev_track.remove_primitive_expected_value("first_named_list_with_evs", "case_0")
    assert set(named_list_ev_track.test_cases) == {"case_1", "case_2"}

def test_remove_one_of_two_for_case_does_not_affect_track_test_cases(named_list_ev_track):
    named_list_ev_track.remove_primitive_expected_value("first_named_list_with_evs", "case_1")
    assert set(named_list_ev_track.test_cases) == {"case_0", "case_1", "case_2"}

def test_replace_variable_test_case_does_not_affect_track_test_cases(named_list_ev_track):
    named_list_ev_track.set_named_list_expected_values("first_named_list_with_evs", "case_0", {})
    assert set(named_list_ev_track.test_cases) == {"case_0", "case_1", "case_2"}

def test_omitting_expected_values_for_designated_list_descendents_raises(named_list_ev_track):
    with pytest.raises(ValueError):
        named_list_ev_track.set_named_list_expected_values("first_named_list_with_evs", "case_0", {
            "steve": {"first_named_list_with_evs_field_1": 17}
        })
