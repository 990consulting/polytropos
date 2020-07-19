import copy
from typing import Dict, cast
from polytropos.actions.changes.stat.cross_sectional.reduce import CrossSectionalCount
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
target_date: VariableId = cast(VariableId, "target_date")


def test_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    change(i_composite)

    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 3
    }
    assert i_composite.content == expected

def test_one_value_missing_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    del i_composite.content["immutable"]["the_list"][0]["the_integer"]

    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 2
    }
    change(i_composite)
    assert i_composite.content == expected

def test_one_value_none_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    i_composite.content["immutable"]["the_list"][0]["the_integer"] = None

    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 2
    }
    change(i_composite)
    assert i_composite.content == expected

def test_all_values_missing_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    for i in range(3):
        del i_composite.content["immutable"]["the_list"][i]["the_integer"]

    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 0
    }
    change(i_composite)
    assert i_composite.content == expected

def test_empty_list_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    del i_composite.content["immutable"]["the_list"]

    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 0
    }
    change(i_composite)
    assert i_composite.content == expected

def test_keyed_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 3
    }
    change(i_composite)
    assert i_composite.content == expected

def test_one_value_missing_keyed_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    del i_composite.content["immutable"]["the_keyed_list"]["green"]["the_decimal"]
    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 2
    }
    change(i_composite)
    assert i_composite.content == expected

def test_one_value_none_keyed_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    i_composite.content["immutable"]["the_keyed_list"]["green"]["the_decimal"] = None
    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 2
    }
    change(i_composite)
    assert i_composite.content == expected

def test_all_values_missing_keyed_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    tkl: Dict = i_composite.content["immutable"]["the_keyed_list"]
    for key in tkl.keys():
        tkl[key] = {}
    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 0
    }
    change(i_composite)
    assert i_composite.content == expected

def test_empty_keyed_list_keyed_list_count(schema, i_composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    i_composite.content["immutable"]["the_keyed_list"] = {}
    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_integer": 0
    }
    change(i_composite)
    assert i_composite.content == expected
