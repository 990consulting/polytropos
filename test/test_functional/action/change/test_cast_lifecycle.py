from collections.abc import Callable
from typing import Dict, List as ListType, Optional, Any

import pytest

from polytropos.actions.changes.cast import Cast
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

primitive_types: ListType[str] = [
    "Integer",
    "Text",
    "Decimal",
    "Unary",
    "Binary",
    "Currency",
    "Phone",
    "Email",
    "URL",
    "Date"
]

@pytest.fixture()
def spec() -> Callable:
    def _spec(prefix: str) -> Dict:
        ret: Dict = {}
        for sort_order, data_type in enumerate(primitive_types):
            var_id: str = "%s_%s" % (prefix, data_type.lower())
            ret[var_id] = {
                "name": "the_%s" % var_id,
                "data_type": data_type,
                "sort_order": sort_order
            }
        return ret
    return _spec

@pytest.fixture()
def schema(spec) -> Schema:
    temporal: Track = Track.build(spec("temporal"), None, "temporal")
    immutable: Track = Track.build(spec("immutable"), None, "immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def content() -> Dict:
    return {
        "201012": {
            "the_temporal_integer": "7",
            "the_temporal_text": "foo",
            "the_temporal_decimal": "-7.3",
            "the_temporal_unary": "X",
            "the_temporal_binary": "true",
            "the_temporal_currency": "27",
            "the_temporal_phone": "(212) 555-1212",
            "the_temporal_email": "joe@example.com",
            "the_temporal_url": "https://www.example.com",
            "the_temporal_date": "2019-07-22"
        },
        "201112": {
            "the_temporal_integer": "",
            "the_temporal_text": "",
            "the_temporal_decimal": "",
            "the_temporal_unary": "",
            "the_temporal_binary": "",
            "the_temporal_currency": "",
            "the_temporal_phone": "",
            "the_temporal_email": "",
            "the_temporal_url": "",
            "the_temporal_date": ""
        },
        "201212": {
            "the_temporal_integer": None,
            "the_temporal_text": None,
            "the_temporal_decimal": None,
            "the_temporal_unary": None,
            "the_temporal_binary": None,
            "the_temporal_currency": None,
            "the_temporal_phone": None,
            "the_temporal_email": None,
            "the_temporal_url": None,
            "the_temporal_date": None
        },
        "201312": {
            "the_temporal_date": "000000"
        },
        "immutable": {
            "the_immutable_integer": "-7",
            "the_immutable_text": "bar",
            "the_immutable_decimal": "7.3",
            "the_immutable_unary": "X",
            "the_immutable_binary": "false",
            "the_immutable_currency": "-27",
            "the_immutable_phone": "abc",
            "the_immutable_email": "123",
            "the_immutable_url": "xyz",
            "the_immutable_date": "201907"
        }
    }

@pytest.fixture()
def composite(schema, content) -> Composite:
    return Composite(schema, content)

@pytest.mark.parametrize("period, var_id, expected", [
    ("201012", "temporal_integer", 7),
    ("201012", "temporal_text", "foo"),
    ("201012", "temporal_decimal", -7.3),
    ("201012", "temporal_unary", True),
    ("201012", "temporal_binary", True),
    ("201012", "temporal_currency", 27.0),
    ("201012", "temporal_phone", "(212) 555-1212"),
    ("201012", "temporal_email", "joe@example.com"),
    ("201012", "temporal_url", "https://www.example.com"),
    ("201012", "temporal_date", "2019-07-22"),
    ("201112", "temporal_integer", None),
    ("201112", "temporal_text", None),
    ("201112", "temporal_decimal", None),
    ("201112", "temporal_unary", None),
    ("201112", "temporal_binary", None),
    ("201112", "temporal_currency", None),
    ("201112", "temporal_phone", None),
    ("201112", "temporal_email", None),
    ("201112", "temporal_url", None),
    ("201112", "temporal_date", None),
    ("201212", "temporal_integer", None),
    ("201212", "temporal_text", None),
    ("201212", "temporal_decimal", None),
    ("201212", "temporal_unary", None),
    ("201212", "temporal_binary", None),
    ("201212", "temporal_currency", None),
    ("201212", "temporal_phone", None),
    ("201212", "temporal_email", None),
    ("201212", "temporal_url", None),
    ("201212", "temporal_date", None),
    ("201312", "temporal_date", None)
])
def test_cast_temporal(schema, composite, period: str, var_id: str, expected: Optional[Any]):
    cast: Cast = Cast(schema, {})
    cast(composite)
    actual: Optional[Any] = composite.get_observation(var_id, period)
    if actual != expected:
        print("breakpoint")
    assert actual == expected

@pytest.mark.parametrize("var_id, expected", [
    ("immutable_integer", -7),
    ("immutable_text", "bar"),
    ("immutable_decimal", 7.3),
    ("immutable_unary", True),
    ("immutable_binary", False),
    ("immutable_currency", -27.0),
    ("immutable_phone", "abc"),  # String-like fields should not be modified
    ("immutable_email", "123"),    # String-like fields should not be modified
    ("immutable_url", "xyz"),
    ("immutable_date", "2019-07-01"),
])
def test_cast_immutable(schema, composite, var_id: str, expected: Optional[Any]):
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.get_immutable(var_id) == expected

def test_cast_complex():
    spec: Dict = {
        "root_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0
        },
        "int_in_list": {
            "name": "some_int",
            "data_type": "Integer",
            "parent": "root_list",
            "sort_order": 0
        },
        "folder_in_list": {
            "name": "the_folder",
            "data_type": "Folder",
            "parent": "root_list",
            "sort_order": 1
        },
        "binary_in_folder_in_list": {
            "name": "some_binary",
            "data_type": "Binary",
            "parent": "folder_in_list",
            "sort_order": 0
        },
        "named_list_in_folder_in_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "parent": "folder_in_list",
            "sort_order": 1
        },
        "date_in_named_list_in_folder_in_list": {
            "name": "some_date",
            "data_type": "Date",
            "parent": "named_list_in_folder_in_list",
            "sort_order": 0
        }
    }
    immutable: Track = Track.build(spec, None, "immutable")
    temporal: Track = Track.build({}, None, "temporal")
    schema: Schema = Schema(temporal, immutable)
    content: Dict = {
        "immutable": {
            "the_list": [
                {
                    "some_int": "-0",
                    "the_folder": {
                        "some_binary": "1",
                        "the_named_list": {
                            "bob": {
                                "some_date": "2001-01-01"
                            },
                            "susan": {
                                "some_date": "000000"
                            }
                        }
                    }
                },
                {
                    "some_int": "74",
                    "the_folder": {
                        "some_binary": "FaLsE",
                        "the_named_list": {
                            "bob": {
                                "some_date": "201712"
                            },
                            "susan": {}
                        }
                    }
                }
            ]
        }
    }
    expected: Dict = {
        "immutable": {
            "the_list": [
                {
                    "some_int": 0,
                    "the_folder": {
                        "some_binary": True,
                        "the_named_list": {
                            "bob": {
                                "some_date": "2001-01-01"
                            },
                            "susan": {
                                "some_date": None
                            }
                        }
                    }
                },
                {
                    "some_int": 74,
                    "the_folder": {
                        "some_binary": False,
                        "the_named_list": {
                            "bob": {
                                "some_date": "2017-12-01"
                            },
                            "susan": {}
                        }
                    }
                }
            ]
        }

    }
    composite: Composite = Composite(schema, content)
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.content == expected

@pytest.fixture()
def nested_track() -> Track:
    spec: Dict = {
        "root_folder": {
            "name": "folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "int_in_folder": {
            "name": "some_int",
            "data_type": "Integer",
            "parent": "root_folder",
            "sort_order": 0
        },
        "list_in_folder": {
            "name": "list",
            "data_type": "List",
            "parent": "root_folder",
            "sort_order": 1
        },
        "int_in_list": {
            "name": "some_int",
            "data_type": "Integer",
            "parent": "list_in_folder",
            "sort_order": 0
        },
        "qc": {
            "name": "qc",
            "data_type": "Folder",
            "sort_order": 1
        }
    }
    return Track.build(spec, None, "nested")

def test_cast_nonexistent(nested_track):
    """If Cast encounters an unknown variable, it records an exception and then leaves it unaltered. If the unknown
    variable is nested inside one or more lists or named lists, only the last example of the error is recorded as an
    exception."""
    temporal: Track = Track.build({}, None, "temporal")
    schema: Schema = Schema(temporal, nested_track)
    content: Dict = {
        "immutable": {
            "fake_in_root": "0",
            "folder": {
                "some_int": "5",
                "fake_in_folder": "7",
                "list": [
                    {
                        "some_int": "42",
                        "fake_in_list": "this will not appear"  # When there's a list, only the last example is recorded
                    },
                    {
                        "some_int": "24",
                        "fake_in_list": "this will appear in the exceptions"
                    }
                ]
            }
        }
    }
    expected: Dict = {
        "immutable": {
            "fake_in_root": "0",
            "folder": {
                "some_int": 5,
                "fake_in_folder": "7",
                "list": [
                    {
                        "some_int": 42,
                        "fake_in_list": "this will not appear"  # When there's a list, only the last example is recorded
                    },
                    {
                        "some_int": 24,
                        "fake_in_list": "this will appear in the exceptions"
                    }
                ]
            },
            "qc": {
                "_exceptions": {
                    "unknown_vars": {
                        "fake_in_root": "0",
                        "folder": {
                            "fake_in_folder": "7",
                            "list": {
                                "fake_in_list": "this will appear in the exceptions"
                            }
                        }
                    }
                }
            }
        }
    }
    composite: Composite = Composite(schema, content)
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.content == expected

def test_underscore_variables_ignored():
    spec: Dict = {
        "binary_in_root": {
            "name": "the_binary",
            "data_type": "Binary",
            "sort_order": 0
        }
    }
    immutable: Track = Track.build(spec, None, "immutable")
    temporal: Track = Track.build({}, None, "temporal")
    schema: Schema = Schema(temporal, immutable)
    content: Dict = {
        "immutable": {
            "the_binary": "true",
            "_something_else": "should be ignored"
        }
    }
    expected: Dict = {
        "immutable": {
            "the_binary": True,
            "_something_else": "should be ignored"
        }
    }
    composite: Composite = Composite(schema, content)
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.content == expected

def test_underscore_folders_ignored():
    spec: Dict = {
        "binary_in_root": {
            "name": "the_binary",
            "data_type": "Binary",
            "sort_order": 0
        }
    }
    immutable: Track = Track.build(spec, None, "immutable")
    temporal: Track = Track.build({}, None, "temporal")
    schema: Schema = Schema(temporal, immutable)
    content: Dict = {
        "immutable": {
            "the_binary": "true",
            "_folder": {
                "foo": "shouldn't matter",
                "bar": "also shouldn't matter"
            }
        }
    }
    expected: Dict = {
        "immutable": {
            "the_binary": True,
            "_folder": {
                "foo": "shouldn't matter",
                "bar": "also shouldn't matter"
            }
        }
    }
    composite: Composite = Composite(schema, content)
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.content == expected

def test_cast_nested_illegal_value(nested_track):
    """If a primitive contains an unintelligible value, it is deleted from the dataset, since we don't want to falsely
    report explicit null and its presence could break downstream steps. The value is recorded as an exception. If the
    exception occurs inside a list, only the last example is recorded."""

    temporal: Track = Track.build({}, None, "temporal")
    schema: Schema = Schema(temporal, nested_track)
    content: Dict = {
        "immutable": {
            "folder": {
                "some_int": "foo",
                "list": [
                    {
                        "some_int": "bar",
                    },
                    {
                        "some_int": "baz",
                    },
                    {
                        "some_int": "75"
                    }
                ]
            }
        }
    }
    expected: Dict = {
        "immutable": {
            "folder": {
                "list": [
                    {},
                    {},
                    {
                        "some_int": 75
                    }
                ]
            },
            "qc": {
                "_exceptions": {
                    "cast_errors": {
                        "folder": {
                            "some_int": "foo",
                            "list": {
                                "some_int": "baz"
                            }
                        }
                    }
                }
            }
        }
    }
    composite: Composite = Composite(schema, content)
    cast: Cast = Cast(schema, {})
    cast(composite)
    assert composite.content == expected
