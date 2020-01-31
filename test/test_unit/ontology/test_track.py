from typing import Dict

import pytest

from polytropos.ontology.track import Track, ValidationError
from polytropos.ontology.variable import VariableId


def test_correct_variable_spec():
    spec: Dict = {
        "var1": {
            "name": "name1",
            "data_type": "Text",
            "sort_order": 1
        },
        "var2": {
            "name": "name2",
            "data_type": "Integer",
            "sort_order": 0,
            "metadata": {
                "notes": "notes2"
            }
        }
    }
    track = Track.build(spec, None, "")

    var1 = track[VariableId("var1")]
    assert var1.name == "name1"
    assert var1.data_type == "Text"
    assert var1.sort_order == 1
    assert var1.metadata == {}

    var2 = track[VariableId("var2")]
    assert var2.name == "name2"
    assert var2.data_type == "Integer"
    assert var2.sort_order == 0
    assert var2.metadata == {
        "notes": "notes2"
    }


def test_variable_spec_unexpected_fields():
    spec: Dict = {
        "var2": {
            "name": "name2",
            "data_type": "Integer",
            "sort_order": 0,
            "short_description": "descr3",
            "comment": "comment2",
            "metadata": {
                "notes": "notes2"
            }
        }
    }

    with pytest.raises(ValueError, match=r"unexpected variable fields: \['comment', 'short_description'\]"):
        Track.build(spec, None, "")


def test_variable_spec_one_error():
    spec: Dict = {
        "var1": {
            "name": "name1",
            "data_type": "Text",
            "sort_order": 1
        },
        "var2": {
            "name": "name.2",
            "data_type": "Integer",
            "sort_order": 0,
            "metadata": {
                "notes": "notes2"
            }
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        Track.build(spec, None, "")
    assert len(exc_info.value.errors) == 1
    lines = str(exc_info.value).split("\n")
    assert lines == ["var2: bad name"]


def test_variable_spec_two_errors():
    spec: Dict = {
        "var1": {
            "name": "name/1",
            "data_type": "Text",
            "sort_order": 1
        },
        "var2": {
            "name": "name2",
            "data_type": "Integer",
            "sort_order": 0,
            "parent": "unknown",
            "metadata": {
                "notes": "notes2"
            }
        },
    }
    with pytest.raises(ValidationError) as exc_info:
        Track.build(spec, None, "")
    assert len(exc_info.value.errors) == 2
    lines = str(exc_info.value).split("\n")
    assert lines == [
        "var1: bad name",
        'var2: Variable "var2" lists "unknown" as its parent, but variable doesn\'t exist.',
    ]
