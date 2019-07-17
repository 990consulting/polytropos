import copy
import logging
import warnings
from typing import Dict

import pytest
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.tools.qc.values import CompareVariables

@pytest.fixture
def simple_list_schema(empty_track) -> Schema:
    spec: Dict = {
        "list_in_root": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0
        },
        "text_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "list_in_root",
            "sort_order": 0
        },
        "int_in_folder": {
            "name": "some_number",
            "data_type": "Integer",
            "parent": "list_in_root",
            "sort_order": 1
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

@pytest.fixture
def folder_in_list_schema(empty_track) -> Schema:
    spec: Dict = {
        "list_in_root": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0
        },
        "folder_in_list": {
            "name": "the_folder",
            "data_type": "Folder",
            "parent": "list_in_root",
            "sort_order": 0
        },
        "text_in_folder_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_list",
            "sort_order": 0
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

@pytest.fixture
def list_in_list_schema(empty_track) -> Schema:
    spec: Dict = {
        "list_in_root": {
            "name": "outer",
            "data_type": "List",
            "sort_order": 0
        },
        "list_in_list": {
            "name": "inner",
            "data_type": "List",
            "parent": "list_in_root",
            "sort_order": 0
        },
        "text_in_list_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "list_in_list",
            "sort_order": 0
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

@pytest.fixture
def named_list_in_list_schema(empty_track) -> Schema:
    spec: Dict = {
        "list_in_root": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0
        },
        "named_list_in_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "parent": "list_in_root",
            "sort_order": 0
        },
        "text_in_named_list_in_list": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "named_list_in_list",
            "sort_order": 0
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

# noinspection PyTypeChecker
def test_fixture_none_raises(simple_list_schema):
    """This should simply never happen, because the comparison algorithm should never try to traverse a null as a
    folder."""
    compare: CompareVariables = CompareVariables(simple_list_schema)
    with pytest.raises(AssertionError):
        compare(None, {})

def test_actual_none(simple_list_schema):
    """This could happen, and represents a mismatch."""
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare({}, None) is False

def test_empty_roots(simple_list_schema):
    fixture: Dict = {}
    actual: Dict = {}
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is True

def test_empty_lists(simple_list_schema):
    fixture: Dict = {
        "the_list": []
    }
    actual: Dict = {
        "the_list": []
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is True

def test_identical_simple_lists(simple_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "bar"
            }
        ]
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is True

def test_same_number_empty_elements(simple_list_schema):
    fixture: Dict = {
        "the_list": [{}] * 5
    }
    actual: Dict = {
        "the_list": [{}] * 5
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is True

def test_different_number_empty_elements(simple_list_schema):
    fixture: Dict = {
        "the_list": [{}] * 3
    }
    actual: Dict = {
        "the_list": [{}] * 5
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is False

def test_actual_has_more_elements(simple_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "bar"
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            }
        ]
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is False

def test_fixture_has_more_elements(simple_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "bar"
            }
        ]
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is False

def test_mismatch_in_one_element(simple_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "BAR"
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "bar"
            }
        ]
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is False

# TODO May want to change this in a future release
def test_extra_key_in_actual_element(simple_list_schema):
    """Missing data in the FIXTURE represents lack of test coverage."""

    msg: str = """This test demonstrates a subtle limitation of the expected value comparison (EVC) system. The EVC
    allows a Polytropos user to create fixtures that do not cover every known variable, such that they do not need to be
    identical to the actual output in order to be failure-free. This is equivalent to incomplete test coverage in code.
    Without vastly complicating the EVC system, there is no way to track whether a particular nested variable was
    captured in one list item but not another. DO NOT assume that, because element 1 of the fixture has variable X and
    element 2 does not, the actual value of element 2 explicitly lacks variable X."""
    warnings.warn(msg, RuntimeWarning)

    fixture: Dict = {
        "the_list": [
            {
                "some_text": "foo"
            },
            {
                "some_text": "bar",
                "some_number": 42
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "bar",
                "some_number": 42
            }
        ]
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is True

def test_extra_key_in_fixture_element(simple_list_schema):
    """Missing data that was expected by the fixture represents a mismatch."""
    fixture: Dict = {
        "the_list": [
            {
                "some_text": "foo",
                "some_number": 27
            },
            {
                "some_text": "bar"
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "some_text": "foo"
            },
            {
                "some_text": "bar"
            }
        ]
    }
    compare: CompareVariables = CompareVariables(simple_list_schema)
    assert compare(fixture, actual) is False

def test_nested_folder_identical(folder_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "foo"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(folder_in_list_schema)
    assert compare(fixture, actual) is True

def test_nested_folder_empty_in_fixture(folder_in_list_schema):
    """See warning above about missing data in the fixture."""
    fixture: Dict = {
        "the_list": [
            {
                "the_folder": {}
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "foo"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(folder_in_list_schema)
    assert compare(fixture, actual) is True

def test_nested_folder_empty_in_actual(folder_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "foo"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_folder": {}
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(folder_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_folder_only_in_fixture(folder_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "foo"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {},
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(folder_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_folder_only_in_actual(folder_in_list_schema):
    """See note above about missing data."""
    fixture: Dict = {
        "the_list": [
            {},
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "foo"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(folder_in_list_schema)
    assert compare(fixture, actual) is True

def test_nested_folder_contains_mismatch(folder_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "FOO"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_folder": {
                    "some_text": "foo"
                }
            },
            {
                "the_folder": {
                    "some_text": "bar"
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(folder_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_list_identical(list_in_list_schema):
    fixture: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "C"},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(list_in_list_schema)
    assert compare(fixture, actual) is True

def test_nested_list_actual_has_more_elements(list_in_list_schema):
    fixture: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "D"}
                ]
            }
        ]
    }
    actual: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "C"},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    compare: CompareVariables = CompareVariables(list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_list_fixture_has_more_elements(list_in_list_schema):
    fixture: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "C"},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    actual: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "D"}
                ]
            }
        ]
    }
    compare: CompareVariables = CompareVariables(list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_list_extra_value_in_actual(list_in_list_schema):
    """See warning above about missing data"""
    fixture: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    actual: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "C"},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    compare: CompareVariables = CompareVariables(list_in_list_schema)
    assert compare(fixture, actual) is True

def test_nested_list_extra_value_in_fixture(list_in_list_schema):
    fixture: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {"some_text": "C"},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    actual: Dict = {
        "outer": [
            {
                "inner": [
                    {"some_text": "A"},
                    {"some_text": "B"}
                ]
            },
            {
                "inner": [
                    {},
                    {"some_text": "D"}
                ]
            }
        ]
    }
    compare: CompareVariables = CompareVariables(list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_named_list_identical(named_list_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "rick": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is True

def test_nested_named_list_key_mismatch(named_list_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "rick": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_named_list_extra_value_in_actual_element(named_list_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_named_list_extra_value_in_fixture(named_list_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_named_list_only_in_fixture(named_list_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {}
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is False

def test_nested_named_list_only_in_actual(named_list_in_list_schema):
    """See warnings above about missing data"""
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {}
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is True

def test_named_list_element_only_in_fixture(named_list_in_list_schema):
    """See warnings above about missing data"""
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is False

def test_named_list_element_only_in_actual(named_list_in_list_schema):
    fixture: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    actual: Dict = {
        "the_list": [
            {
                "the_named_list": {
                    "susan": {"some_text": "A"},
                    "bob": {"some_text": "B"}
                }
            },
            {
                "the_named_list": {
                    "steve": {"some_text": "C"},
                    "charlene": {"some_text": "D"}
                }
            }
        ]
    }
    compare: CompareVariables = CompareVariables(named_list_in_list_schema)
    assert compare(fixture, actual) is True

