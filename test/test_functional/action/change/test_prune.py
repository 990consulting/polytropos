import copy
from typing import Dict, Callable
from unittest.mock import MagicMock

import pytest

from polytropos.actions.changes.prune import Prune
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

@pytest.fixture()
def schema() -> Schema:
    return MagicMock(spec=Schema)

@pytest.fixture()
def do_test(schema) -> Callable:
    def _do_test(content: Dict, expected: Dict):
        composite: Composite = Composite(schema, content)
        prune: Prune = Prune(schema, {})
        prune(composite)
        assert content == expected
    return _do_test

def test_trivial_case(do_test):
    do_test({}, {})

def test_acts_on_all_periods(do_test):
    content: Dict = {
        "period_1": {
            "should get pruned": None
        },
        "period_2": {
            "also should get pruned": None
        }
    }
    do_test(content, {})

def test_acts_on_immutable(do_test):
    content: Dict = {
        "period_1": {
            "empty strings aren't pruned": ""
        },
        "immutable": {
            "should get pruned": None
        }
    }
    expected: Dict = {
        "period_1": {
            "empty strings aren't pruned": ""
        }
    }
    do_test(content, expected)

def test_prunes_dicts(do_test):
    content: Dict = {
        "period_1": {
            "should get pruned": {}
        }
    }
    do_test(content, {})

def test_prunes_lists(do_test):
    content: Dict = {
        "period_1": {
            "should get pruned": []
        }
    }
    do_test(content, {})

def test_prunes_complex(do_test):
    content: Dict = {
        "period_1": {
            "a dict containing an empty dict": {
                "an empty dict": {}
            },
            "an empty list": [],
            "the only thing that should survive": "foo"
        }
    }
    expected: Dict = {
        "period_1": {
            "the only thing that should survive": "foo"
        }
    }
    do_test(content, expected)

def test_prunes_inside_lists(do_test):
    content: Dict = {
        "period_1": {
            "a list with some empty nested dicts": [
                {},
                {"a": "b"},
                {"a": {}},
                {"a": {"b": {}}}
            ]
        }
    }
    expected: Dict = {
        "period_1": {
            "a list with some empty nested dicts": [
                {},
                {"a": "b"},
                {},
                {}
            ]
        }

    }
    do_test(content, expected)

def test_a_list_of_empty_dicts_is_not_pruned(do_test):
    content: Dict = {
        "period_1": {
            "a list of empty dicts": [{}] * 5
        }
    }
    expected: Dict = copy.deepcopy(content)
    do_test(content, expected)
