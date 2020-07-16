import copy
from typing import cast, Dict

from polytropos.actions.evolve import Change
from polytropos.actions.changes.stat.cross_sectional.reduce import CrossSectionalSum
from polytropos.ontology.variable import VariableId

list_in_root: VariableId = cast(VariableId, "list_in_root")
target_decimal: VariableId = cast(VariableId, "target_decimal")
int_in_list: VariableId = cast(VariableId, "int_in_list")
kl_in_root: VariableId = cast(VariableId, "keyed_list_in_root")
decimal_in_kl: VariableId = cast(VariableId, "decimal_in_keyed_list")

def test_list_mean(schema, i_composite):
    change: Change = CrossSectionalSum(schema, {}, list_in_root, target_decimal, argument=int_in_list)
    change(i_composite)

    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_decimal": 0.0
    }
    assert i_composite.content == expected

def test_keyed_list_mean(schema, i_composite):
    change: Change = CrossSectionalSum(schema, {}, kl_in_root, target_decimal, argument=decimal_in_kl)
    expected: Dict = copy.deepcopy(i_composite.content)
    expected["immutable"]["targets"] = {
        "target_decimal": 77
    }
    change(i_composite)
    assert i_composite.content == expected
