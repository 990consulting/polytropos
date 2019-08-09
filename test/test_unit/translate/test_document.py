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


def test_value():
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
    assert provider.value(["a"]) == 1
    assert provider.value(["b"]) == 2
    assert provider.value(["c", "d"]) == "1"
    assert provider.value(["c", "e"]) == {"f": "2"}
    assert provider.value(["c", "e", "f"]) == "2"


def test_missing_value():
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
        _ = provider.value(["b"])

    with pytest.raises(KeyError):
        _ = provider.value(["c", "f"])

    with pytest.raises(KeyError):
        _ = provider.value(["c", "e", "z"])

    with pytest.raises(KeyError):
        _ = provider.value(["c", "e", "f", "a"])


def test_variable_value():
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
    assert provider.variable_value(create_variable(["a"])) == 1
    assert provider.variable_value(create_variable(["b"])) == 2
    assert provider.variable_value(create_variable(["d", "c"])) == "1"
    assert provider.variable_value(create_variable(["e", "c"])) == {"f": "2"}
    assert provider.variable_value(create_variable(["f", "e", "c"])) == "2"


def test_missing_variable_value():
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
        _ = provider.variable_value(create_variable(["b"]))

    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(["f", "c"]))

    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(["z", "e", "c"]))

    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(["a", "f", "e", "c"]))


def test_empty_doc():
    doc: Dict[str, Any] = {}

    provider = DocumentValueProvider(doc)

    with pytest.raises(KeyError):
        _ = provider.value(["a"])

    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(["b"]))
