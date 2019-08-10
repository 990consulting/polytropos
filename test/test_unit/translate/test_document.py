from typing import Dict, Any, List
from unittest.mock import Mock

import pytest

from polytropos.actions.translate.__document import DocumentValueProvider, SourceNotFoundException


def create_variable(ancestor_names: List[str]) -> Any:
    def create_variable_mock(name: str) -> Any:
        m = Mock()
        m.name = name
        return m

    ancestors: List[Any] = [create_variable_mock(name) for name in ancestor_names]
    ancestors[0].ancestors.return_value = ancestors
    return ancestors[0]


@pytest.mark.parametrize("path, expected", [
    (["a"], 1),
    (["b"], 2),
    (["c", "d"], "1"),
    (["c", "e"], {"f": "2"}),
    (["c", "e", "f"], "2"),
])
def test_value(path, expected):
    doc: Dict[str, Any] = {
        "a": 1,
        "b": 2,
        "c": {
            "d": "1",
            "e": {
                "f": "2"
            }
        }
    }

    provider = DocumentValueProvider(doc)
    assert provider.value(path) == expected


@pytest.mark.parametrize("path", [
    ["b"],
    ["c", "f"],
    ["c", "e", "z"],
    ["c", "e", "f", "a"],
])
def test_missing_value(path):
    doc: Dict[str, Any] = {
        "a": 1,
        "c": {
            "e": {
                "f": "2"
            }
        }
    }

    provider = DocumentValueProvider(doc)

    with pytest.raises(KeyError):
        _ = provider.value(path)


@pytest.mark.parametrize("ancestor_names, expected", [
    (["a"], 1),
    (["b"], 2),
    (["d", "c"], "1"),
    (["e", "c"], {"f": "2"}),
    (["f", "e", "c"], "2"),
])
def test_variable_value(ancestor_names, expected):
    doc: Dict[str, Any] = {
        "a": 1,
        "b": 2,
        "c": {
            "d": "1",
            "e": {
                "f": "2"
            }
        }
    }

    provider = DocumentValueProvider(doc)
    assert provider.variable_value(create_variable(ancestor_names)) == expected


@pytest.mark.parametrize("ancestor_names", [
    ["b"],
    ["f", "c"],
    ["z", "e", "c"],
    ["a", "f", "e", "c"],
])
def test_missing_variable_value(ancestor_names):
    doc: Dict[str, Any] = {
        "a": 1,
        "c": {
            "e": {
                "f": "2"
            }
        }
    }

    provider = DocumentValueProvider(doc)
    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(ancestor_names))


def test_empty_doc():
    doc: Dict[str, Any] = {}

    provider = DocumentValueProvider(doc)

    with pytest.raises(KeyError):
        _ = provider.value(["a"])

    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(["b"]))
