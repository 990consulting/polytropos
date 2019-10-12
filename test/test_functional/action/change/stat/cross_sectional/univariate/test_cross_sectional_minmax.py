import copy
from typing import Dict, cast

import pytest

from polytropos.actions.changes.stat.cross_sectional.univariate import CrossSectionalMaximum, CrossSectionalMinimum
from polytropos.actions.evolve import Change
from polytropos.ontology.variable import VariableId

list_in_root: VariableId = cast(VariableId, "list_in_root")
int_in_list: VariableId = cast(VariableId, "int_in_list")
target_int: VariableId = cast(VariableId, "target_int")
target_text: VariableId = cast(VariableId, "target_text")
text_in_list: VariableId = cast(VariableId, "text_in_list")
kl_in_root: VariableId = cast(VariableId, "keyed_list_in_root")
text_in_kl: VariableId = cast(VariableId, "text_in_keyed_list")
decimal_in_kl: VariableId = cast(VariableId, "decimal_in_keyed_list")
target_decimal: VariableId = cast(VariableId, "target_decimal")

def test_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    change(composite)

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 75,
        "target_text": "a"
    }
    assert composite.content == expected

def test_list_max_no_identifier_yes_id_target_raises(schema, composite):
    with pytest.raises(ValueError):
        CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, None, target_text)

def test_list_max_yes_identifier_no_target_raises(schema, composite):
    with pytest.raises(ValueError):
        CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, None)

def test_disable_identifier_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int)

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 75
    }
    change(composite)
    assert composite.content == expected

def test_identifier_missing_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    del composite.content["populated"]["the_list"][0]["the_text"]

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 75
    }
    change(composite)
    assert composite.content == expected

def test_identifier_none_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    composite.content["populated"]["the_list"][0]["the_text"] = None

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 75,
        "target_text": None
    }
    change(composite)
    assert composite.content == expected

def test_one_value_missing_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    del composite.content["populated"]["the_list"][0]["the_integer"]

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 0,
        "target_text": "b"
    }
    change(composite)
    assert composite.content == expected

def test_one_value_none_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    composite.content["populated"]["the_list"][0]["the_integer"] = None

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 0,
        "target_text": "b"
    }
    change(composite)
    assert composite.content == expected

def test_all_values_missing_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    for i in range(3):
        del composite.content["populated"]["the_list"][i]["the_integer"]

    expected: Dict = copy.deepcopy(composite.content)
    change(composite)
    assert composite.content == expected

def test_empty_list_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    del composite.content["populated"]["the_list"]

    expected: Dict = copy.deepcopy(composite.content)
    change(composite)
    assert composite.content == expected

def test_keyed_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, target_text)
    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_decimal": 100.6,
        "target_text": "green"
    }
    change(composite)
    assert composite.content == expected

def test_keyed_list_explicit_identifier_raises(schema):
    with pytest.raises(ValueError):
        CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, text_in_kl)

def test_keyed_list_max_no_id_target(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, None)
    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_decimal": 100.6
    }
    change(composite)
    assert composite.content == expected

def test_one_value_missing_keyed_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, target_text)
    del composite.content["populated"]["the_keyed_list"]["green"]["the_decimal"]
    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_decimal": 0.7,
        "target_text": "red"
    }
    change(composite)
    assert composite.content == expected

def test_one_value_none_keyed_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, target_text)
    composite.content["populated"]["the_keyed_list"]["green"]["the_decimal"] = None
    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_decimal": 0.7,
        "target_text": "red"
    }
    change(composite)
    assert composite.content == expected

def test_all_values_missing_keyed_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, target_text)
    tkl: Dict = composite.content["populated"]["the_keyed_list"]
    for key in tkl.keys():
        tkl[key] = {}
    expected: Dict = copy.deepcopy(composite.content)
    change(composite)
    assert composite.content == expected

def test_empty_keyed_list_keyed_list_max(schema, composite):
    change: Change = CrossSectionalMaximum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, target_text)
    composite.content["populated"]["the_keyed_list"] = {}
    expected: Dict = copy.deepcopy(composite.content)
    change(composite)
    assert composite.content == expected

def test_list_min(schema, composite):
    change: Change = CrossSectionalMinimum(schema, {}, list_in_root, int_in_list, target_int, text_in_list, target_text)
    change(composite)

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": -75,
        "target_text": "c"
    }
    assert composite.content == expected

def test_keyed_list_min(schema, composite):
    change: Change = CrossSectionalMinimum(schema, {}, kl_in_root, decimal_in_kl, target_decimal, None, target_text)
    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_decimal": -24.3,
        "target_text": "blue"
    }
    change(composite)
    assert composite.content == expected
