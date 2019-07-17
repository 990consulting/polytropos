import copy
from typing import Dict

import pytest
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.tools.qc.values import CompareVariables


@pytest.fixture
def simple_schema(empty_track) -> Schema:
    spec: Dict = {
        "text_in_root": {
            "name": "some_text",
            "data_type": "Text",
            "sort_order": 0
        },
        "folder_in_root": {
            "name": "the_folder",
            "data_type": "Folder",
            "sort_order": 1
        },
        "text_in_folder": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_root",
            "sort_order": 0
        },
        "int_in_folder": {
            "name": "some_number",
            "data_type": "Integer",
            "parent": "folder_in_root",
            "sort_order": 1
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

@pytest.fixture
def nested_folder_schema(empty_track) -> Schema:
    spec: Dict = {
        "text_in_root": {
            "name": "some_text",
            "data_type": "Text",
            "sort_order": 0
        },
        "folder_in_root": {
            "name": "parent",
            "data_type": "Folder",
            "sort_order": 1
        },
        "text_outer": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_root",
            "sort_order": 0
        },
        "folder_in_folder": {
            "name": "child",
            "data_type": "Folder",
            "parent": "folder_in_root",
            "sort_order": 1
        },
        "text_middle": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_folder",
            "sort_order": 0
        },
        "folder_in_folder_in_folder": {
            "name": "grandchild",
            "data_type": "Folder",
            "parent": "folder_in_folder",
            "sort_order": 1
        },
        "text_inner": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "folder_in_folder_in_folder",
            "sort_order": 0
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

@pytest.fixture
def list_in_nested_folder_schema(empty_track) -> Schema:
    spec: Dict = {
        "folder_in_root": {
            "name": "parent",
            "data_type": "Folder",
            "sort_order": 0
        },
        "folder_in_folder": {
            "name": "child",
            "data_type": "Folder",
            "parent": "folder_in_root",
            "sort_order": 0
        },
        "folder_in_folder_in_folder": {
            "name": "grandchild",
            "data_type": "Folder",
            "parent": "folder_in_folder",
            "sort_order": 0
        },
        "nested_list": {
            "name": "the_list",
            "data_type": "List",
            "parent": "folder_in_folder_in_folder",
            "sort_order": 0
        },
        "list_text": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "nested_list",
            "sort_order": 0
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

@pytest.fixture
def named_list_in_nested_folder_schema(empty_track) -> Schema:
    spec: Dict = {
        "folder_in_root": {
            "name": "parent",
            "data_type": "Folder",
            "sort_order": 0
        },
        "folder_in_folder": {
            "name": "child",
            "data_type": "Folder",
            "parent": "folder_in_root",
            "sort_order": 0
        },
        "folder_in_folder_in_folder": {
            "name": "grandchild",
            "data_type": "Folder",
            "parent": "folder_in_folder",
            "sort_order": 0
        },
        "nested_named_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "parent": "folder_in_folder_in_folder",
            "sort_order": 0
        },
        "named_list_text": {
            "name": "some_text",
            "data_type": "Text",
            "parent": "nested_named_list",
            "sort_order": 0
        }
    }
    test_track: Track = Track.build(spec, None, "")
    return Schema(test_track, empty_track)

# noinspection PyTypeChecker
def test_fixture_none_raises(simple_schema):
    """This should simply never happen, because the comparison algorithm should never try to traverse a null as a
    folder."""
    compare: CompareVariables = CompareVariables(simple_schema)
    with pytest.raises(AssertionError):
        compare(None, {})

def test_actual_none(simple_schema):
    """This could happen, and represents a mismatch."""
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare({}, None) is False

def test_empty_roots(simple_schema):
    """Empty roots are identical and therefore match."""
    fixture: Dict = {}
    actual: Dict = {}
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_empty_folders(simple_schema):
    """Empty folders are identical and therefore match."""
    fixture: Dict = {
        "the_folder": {}
    }
    actual: Dict = {
        "the_folder": {}
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_identical_folders(simple_schema):
    fixture: Dict = {
        "the_folder": {
            "some_text": "Foo",
            "some_number": 75
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_fixture_has_extra_in_folder(simple_schema):
    """Missing data that was expected by the fixture represents a mismatch."""
    fixture: Dict = {
        "some_text": "Foo",
        "some_number": 75
    }
    actual: Dict = {
        "some_text": "Foo"
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is False

def test_actual_has_extra_in_folder(simple_schema):
    """Missing data in the FIXTURE represents lack of test coverage."""
    fixture: Dict = {
        "some_text": "Foo"
    }
    actual: Dict = {
        "some_text": "Foo",
        "some_number": 75
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_singly_nested_identical(simple_schema):
    fixture: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "Bar"
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_fixture_has_extra_out_of_folder(simple_schema):
    """Missing data that was expected by the fixture represents a mismatch."""
    fixture: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "Bar"
        }
    }
    actual: Dict = {
        "the_folder": {
            "some_text": "Bar"
        }
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is False

def test_actual_has_extra_out_of_folder(simple_schema):
    """Missing data in the FIXTURE represents lack of test coverage."""
    fixture: Dict = {
        "the_folder": {
            "some_text": "Bar"
        }
    }
    actual: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "Bar"
        }
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_only_fixture_has_folder(simple_schema):
    """Missing data that was expected by the fixture represents a mismatch."""
    fixture: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "Bar"
        }
    }
    actual: Dict = {
        "some_text": "Foo"
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is False

def test_only_actual_has_folder(simple_schema):
    """Missing data in the FIXTURE represents lack of test coverage."""
    fixture: Dict = {
        "some_text": "Foo",
    }
    actual: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "Bar"
        }
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_only_fixture_has_folder_empty(simple_schema):
    """Missing data that was expected by the fixture represents a mismatch."""
    fixture: Dict = {
        "some_text": "Foo",
        "the_folder": {}
    }
    actual: Dict = {
        "some_text": "Foo"
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is False

def test_only_actual_has_folder_empty(simple_schema):
    """Missing data in the FIXTURE represents lack of test coverage."""
    fixture: Dict = {
        "some_text": "Foo",
    }
    actual: Dict = {
        "some_text": "Foo",
        "the_folder": {}
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is True

def test_non_nested_mismatch(simple_schema):
    fixture: Dict = {
        "some_text": "Foo"
    }
    actual: Dict = {
        "some_text": "Bar"
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is False

def test_singly_nested_mismatch(simple_schema):
    fixture: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "X"
        }
    }
    actual: Dict = {
        "some_text": "Foo",
        "the_folder": {
            "some_text": "Y"
        }
    }
    compare: CompareVariables = CompareVariables(simple_schema)
    assert compare(fixture, actual) is False

def test_triply_nested_folder_identical(nested_folder_schema):
    fixture: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(nested_folder_schema)
    assert compare(fixture, actual) is True

def test_triply_nested_folder_fixture_has_extra(nested_folder_schema):
    fixture: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    actual: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {}
            }
        }
    }
    compare: CompareVariables = CompareVariables(nested_folder_schema)
    assert compare(fixture, actual) is False

def test_triply_nested_folder_actual_has_extra(nested_folder_schema):
    actual: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    fixture: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y"
            }
        }
    }
    compare: CompareVariables = CompareVariables(nested_folder_schema)
    assert compare(fixture, actual) is True

def test_triply_nested_folder_mismatch(nested_folder_schema):
    fixture: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    actual: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "A"
                }
            }
        }
    }
    compare: CompareVariables = CompareVariables(nested_folder_schema)
    assert compare(fixture, actual) is False

def test_nested_mismatch_on_lower_level(nested_folder_schema):
    fixture: Dict = {
        "some_text": "Foo",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    actual: Dict = {
        "some_text": "Bar",
        "parent": {
            "some_text": "X",
            "child": {
                "some_text": "Y",
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    compare: CompareVariables = CompareVariables(nested_folder_schema)
    assert compare(fixture, actual) is False

def test_list_in_folder_mismatch(list_in_nested_folder_schema):
    fixture: Dict = {
        "parent": {
            "child": {
                "grandchild": {
                    "the_list": [
                        {
                            "some_text": "Foo"
                        }
                    ]
                }
            }
        }
    }
    actual: Dict = {
        "parent": {
            "child": {
                "grandchild": {
                    "the_list": [
                        {
                            "some_text": "Bar"
                        }
                    ]
                }
            }
        }
    }
    compare: CompareVariables = CompareVariables(list_in_nested_folder_schema)
    assert compare(fixture, actual) is False

def test_list_in_folder_identical(list_in_nested_folder_schema):
    fixture: Dict = {
        "parent": {
            "child": {
                "grandchild": {
                    "the_list": [
                        {
                            "some_text": "Foo"
                        }
                    ]
                }
            }
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(list_in_nested_folder_schema)
    assert compare(fixture, actual) is True

def test_named_list_in_folder_mismatch(named_list_in_nested_folder_schema):
    fixture: Dict = {
        "parent": {
            "child": {
                "grandchild": {
                    "the_named_list": {
                        "Steve": {
                            "some_text": "Foo"
                        }
                    }
                }
            }
        }
    }
    actual: Dict = {
        "parent": {
            "child": {
                "grandchild": {
                    "the_named_list": {
                        "Steve": {
                            "some_text": "Bar"
                        }
                    }
                }
            }
        }
    }
    compare: CompareVariables = CompareVariables(named_list_in_nested_folder_schema)
    assert compare(fixture, actual) is False

def test_named_list_in_folder_identical(named_list_in_nested_folder_schema):
    fixture: Dict = {
        "parent": {
            "child": {
                "grandchild": {
                    "the_named_list": {
                        "Steve": {
                            "some_text": "Foo"
                        }
                    }
                }
            }
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(named_list_in_nested_folder_schema)
    assert compare(fixture, actual) is True

def test_unrecognized_folder_raises(simple_schema):
    fixture: Dict = {
        "not_a_thing": {
            "some_text": "Bar"
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(simple_schema)
    with pytest.raises(ValueError):
        compare(fixture, actual)

def test_unrecognized_nested_folder_raises(nested_folder_schema):
    fixture: Dict = {
        "parent": {
            "not_a_thing": {
                "grandchild": {
                    "some_text": "Z"
                }
            }
        }
    }
    actual: Dict = copy.deepcopy(fixture)
    compare: CompareVariables = CompareVariables(nested_folder_schema)
    with pytest.raises(ValueError):
        compare(fixture, actual)

