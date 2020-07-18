"""Test to make sure that, if the target is part of the ad-hoc subject group, its original value gets properly included
and then overwritten."""
import copy
from typing import Dict, Callable, List, cast

import pytest

from polytropos.actions.changes.stat.cross_sectional.reduce import CrossSectionalSum
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def ah_schema() -> Schema:
    t_spec: Dict = {
        "ad_hoc_{}".format(idx): {
            "name": "ad_hoc_{}".format(idx),
            "data_type": "Decimal",
            "sort_order": idx
        } for idx in range(4)
    }
    temporal: Track = Track(t_spec, None, "temporal")
    immutable: Track = Track({}, None, "immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def do_test(ah_schema: Schema) -> Callable:
    def _do_test(content: Dict, expected: Dict) -> None:
        composite: Composite = Composite(ah_schema, content)
        subjects: List[VariableId] = [cast(VariableId, "ad_hoc_{}".format(idx)) for idx in range(4)]
        target: VariableId = subjects[0]
        change: CrossSectionalSum = CrossSectionalSum(ah_schema, {}, subjects, value_target=target)
        change(composite)
        assert composite.content == expected
    return _do_test

def test_nothing_populated(do_test):
    content: Dict = {
        "the_period": {}
    }
    expected: Dict = copy.deepcopy(content)
    expected["the_period"]["ad_hoc_0"] = 0.0
    do_test(content, expected)

def test_target_not_populated(do_test):
    content: Dict = {
        "the_period": {
            "ad_hoc_1": 1.0,
            "ad_hoc_2": 2.5
        }
    }
    expected: Dict = copy.deepcopy(content)
    expected["the_period"]["ad_hoc_0"] = 3.5
    do_test(content, expected)

def test_only_target_populated(do_test):
    content: Dict = {
        "the_period": {
            "ad_hoc_0": -17.6
        }
    }
    expected: Dict = copy.deepcopy(content)
    do_test(content, expected)

def test_all_populated(do_test):
    content: Dict = {
        "the_period": {
            "ad_hoc_0": -17.6,
            "ad_hoc_1": 1.0,
            "ad_hoc_2": 2.5,
            "ad_hoc_3": -4.0
        }
    }
    expected: Dict = copy.deepcopy(content)
    expected["the_period"]["ad_hoc_0"] = -18.1
    do_test(content, expected)

def test_two_periods(do_test):
    content: Dict = {
        "period_1": {},
        "period_2": {
            "ad_hoc_0": -4.5,
            "ad_hoc_1": 1.0,
            "ad_hoc_2": 2.5
        }
    }
    expected: Dict = copy.deepcopy(content)
    expected["period_1"]["ad_hoc_0"] = 0.0
    expected["period_2"]["ad_hoc_0"] = -1.0
    do_test(content, expected)