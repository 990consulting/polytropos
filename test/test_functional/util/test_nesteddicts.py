import pytest

from polytropos.util import nesteddicts
from pytest import raises, mark
from typing import *

def _do_get_test(data: Dict, spec: List[str], expected: Optional[str] = "expected", **kwargs):
    actual: Any = nesteddicts.get(data, spec, **kwargs)
    assert actual == expected

def test_empty_spec_returns_self():
    data: Dict = {
        "a": {
            "b": {
                "c": "expected"
            }
        }
    }
    spec: List[str] = []
    expected: Dict = data
    actual: Any = nesteddicts.get(data, spec)
    assert actual == expected

def test_get_no_nesting():
    data: Dict = {
        "a": "expected"
    }
    spec: List[str] = ["a"]
    _do_get_test(data, spec)

def test_get_nested():
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {
        "a": {
            "b": {
                "c": "expected"
            }
        }
    }
    _do_get_test(data, spec)

def test_get_missing_default():
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {
        "a": {
            "b": {
                "d": "not expected"
            }
        }
    }
    _do_get_test(data, spec, default="expected")

def test_get_missing_default_is_none():
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {
        "a": {
            "b": {
                "d": "not expected"
            }
        }
    }
    _do_get_test(data, spec, default=None, accept_none=True, expected=None)

def test_get_missing_nodefault_raises():
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {
        "a": {
            "b": {
                "d": "not expected"
            }
        }
    }
    with raises(nesteddicts.MissingDataError):
        _do_get_test(data, spec)

def test_get_actually_none():
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {
        "a": {
            "b": {
                "c": None
            }
        }
    }
    _do_get_test(data, spec, expected=None)

def test_get_empty():
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {}
    _do_get_test(data, spec, default="expected")

@mark.parametrize("default", [None, "non-null"])
def test_get_not_nested(default: Optional[str]):
    spec: List[str] = ["a", "b", "c"]
    data: Dict = {
        "a": {
            "b": "I'm supposed to be nested, but I'm not"
        }
    }
    with raises(nesteddicts.IncompleteNestingError):
        nesteddicts.get(data, spec, default=default)

def test_put():
    target: Dict = {}
    spec: List[str] = ["a", "b", "c"]
    value: str = "value"
    nesteddicts.put(target, spec, value)

    expected: Dict = {"a": {"b": {"c": "value"}}}
    assert expected == target

def test_put_tree_exists():
    target: Dict = {"a": {"b": {"c": "old value"}}}
    spec: List[str] = ["a", "b", "c"]
    value: str = "new value"
    nesteddicts.put(target, spec, value)

    expected: Dict = {"a": {"b": {"c": "new value"}}}
    assert expected == target

def test_put_parent_missing():
    target: Dict = {"a": {}}
    spec: List[str] = ["a", "b", "c"]
    value: str = "value"
    nesteddicts.put(target, spec, value)

    expected: Dict = {"a": {"b": {"c": "value"}}}
    assert expected == target

def test_put_incomplete_nesting():
    target: Dict = {"a": "b"}
    spec: List[str] = ["a", "b", "c"]
    value: str = "value"
    with raises(nesteddicts.IncompleteNestingError):
        nesteddicts.put(target, spec, value)

def test_delete_passthru():
    target: Dict = {}
    spec: List[str] = ["a", "b", "c"]
    nesteddicts.delete(target, spec)
    assert {} == target

@mark.parametrize("target", [
   {"a": {"b": {"c": "old value"}}},
   {"a": {"b": {}}}
])
def test_delete(target: Dict):
    spec: List[str] = ["a", "b", "c"]
    nesteddicts.delete(target, spec)

    expected: Dict = {"a": {"b": {}}}
    assert expected == target

def test_pop_gets_value():
    target: Dict = {"a": {"b": {"c": "value"}}}
    spec: List[str] = ["a", "b", "c"]
    expected: str = "value"
    actual: str = nesteddicts.pop(target, spec)
    assert actual == expected

def test_getpop_deletes():
    target: Dict = {"a": {"b": {"c": "value"}}}
    spec: List[str] = ["a", "b", "c"]
    nesteddicts.pop(target, spec)
    expected: Dict = {"a": {"b": {}}}
    assert expected == target

def test_getpop_missing_returns_default():
    target: Dict = {"a": {"b": {}}}
    spec: List[str] = ["a", "b", "c"]
    expected: str = "value"
    actual: str = nesteddicts.pop(target, spec, default="value")
    assert actual == expected

def test_getpop_missing_no_delete():
    target: Dict = {"a": {"b": {}}}
    spec: List[str] = ["a", "b", "c"]
    expected: Dict = target.copy()
    nesteddicts.pop(target, spec, default="value")
    assert expected == target

def test_getpop_no_default_raises():
    target: Dict = {"a": {"b": {}}}
    spec: List[str] = ["a", "b", "c"]
    with raises(nesteddicts.MissingDataError):
        nesteddicts.pop(target, spec)
