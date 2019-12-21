import copy
from typing import Dict, cast, List

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

from polytropos.actions.changes.stat.cross_sectional.univariate import CrossSectionalCount
from polytropos.actions.evolve import Change
from polytropos.ontology.track import Track
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

@pytest.fixture()
def schema(spec_body) -> Schema:
    temporal: Track = Track.build(spec_body, None, "temporal")
    immutable: Track = Track.build({}, None, "immutable")
    schema: Schema = Schema(temporal, immutable)
    return schema

@pytest.fixture()
def composite(schema, content_body) -> Composite:
    content: Dict = {
        "populated": content_body,
        "unpopulated": {}
    }
    return Composite(schema, content)

def test_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    change(composite)

    expected: Dict = copy.deepcopy(composite.content)
    expected["populated"]["targets"] = {
        "target_integer": 3
    }
    assert composite.content == expected

def test_one_value_missing_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    del composite.content["populated"]["the_list"][0]["the_integer"]

    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 2
    }
    change(composite)
    assert composite.content == expected

def test_one_value_none_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    composite.content["populated"]["the_list"][0]["the_integer"] = None

    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 2
    }
    change(composite)
    assert composite.content == expected

def test_all_values_missing_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    for i in range(3):
        del composite.content["populated"]["the_list"][i]["the_integer"]

    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 0
    }
    change(composite)
    assert composite.content == expected

def test_empty_list_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, list_in_root, target_int, argument=int_in_list)
    del composite.content["populated"]["the_list"]

    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 0
    }
    change(composite)
    assert composite.content == expected

def test_keyed_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 3
    }
    change(composite)
    assert composite.content == expected

def test_one_value_missing_keyed_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    del composite.content["populated"]["the_keyed_list"]["green"]["the_decimal"]
    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 2
    }
    change(composite)
    assert composite.content == expected

def test_one_value_none_keyed_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    composite.content["populated"]["the_keyed_list"]["green"]["the_decimal"] = None
    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 2
    }
    change(composite)
    assert composite.content == expected

def test_all_values_missing_keyed_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    tkl: Dict = composite.content["populated"]["the_keyed_list"]
    for key in tkl.keys():
        tkl[key] = {}
    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 0
    }
    change(composite)
    assert composite.content == expected

def test_empty_keyed_list_keyed_list_count(schema, composite):
    change: Change = CrossSectionalCount(schema, {}, kl_in_root, target_int, argument=decimal_in_kl)
    composite.content["populated"]["the_keyed_list"] = {}
    expected: Dict = copy.deepcopy(composite.content)
    expected["unpopulated"]["targets"] = {
        "target_integer": 0
    }
    expected["populated"]["targets"] = {
        "target_integer": 0
    }
    change(composite)
    assert composite.content == expected
