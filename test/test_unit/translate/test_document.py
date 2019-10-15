from typing import Dict, Any, List
from unittest.mock import Mock

import pytest

from polytropos.actions.translate.__document import DocumentValueProvider, SourceNotFoundException
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider


def create_variable(ancestor_names: List[str]) -> Any:
    def create_variable_mock(name: str) -> Any:
        m = Mock()
        m.var_id = "id_" + name
        m.name = name
        return m

    ancestors: List[Any] = [create_variable_mock(name) for name in ancestor_names]
    ancestors[0].ancestors.return_value = ancestors
    return ancestors[0]


@pytest.mark.parametrize("create_document_value_provider", [DocumentValueProvider, TraceDocumentValueProvider])
@pytest.mark.parametrize("path, expected", [
    (["a"], 1),
    (["b"], 2),
    (["c", "d"], "1"),
    (["c", "e"], {"f": "2"}),
    (["c", "e", "f"], "2"),
])
def test_value(create_document_value_provider, path, expected):
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

    provider = create_document_value_provider(doc)
    assert provider.value(path) == expected


@pytest.mark.parametrize("create_document_value_provider", [DocumentValueProvider, TraceDocumentValueProvider])
@pytest.mark.parametrize("path", [
    ["b"],
    ["c", "f"],
    ["c", "e", "z"],
    ["c", "e", "f", "a"],
])
def test_missing_value(create_document_value_provider, path):
    doc: Dict[str, Any] = {
        "a": 1,
        "c": {
            "e": {
                "f": "2"
            }
        }
    }

    provider = create_document_value_provider(doc)

    with pytest.raises(KeyError):
        _ = provider.value(path)


@pytest.mark.parametrize("index, create_document_value_provider", enumerate([DocumentValueProvider, TraceDocumentValueProvider]))
@pytest.mark.parametrize("ancestor_names, expected", [
    (["a"], (1, "id_a")),
    (["b"], (2, "id_b")),
    (["d", "c"], ("1", "id_d")),
    (["e", "c"], ({"f": "2"}, "id_e")),
    (["f", "e", "c"], ("2", "id_f")),
])
def test_variable_value(index, create_document_value_provider, ancestor_names, expected):
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

    provider = create_document_value_provider(doc)
    assert provider.variable_value(create_variable(ancestor_names)) == expected[index]


@pytest.mark.parametrize("create_document_value_provider", [DocumentValueProvider, TraceDocumentValueProvider])
@pytest.mark.parametrize("ancestor_names", [
    ["b"],
    ["f", "c"],
    ["z", "e", "c"],
    ["a", "f", "e", "c"],
])
def test_missing_variable_value(create_document_value_provider, ancestor_names):
    doc: Dict[str, Any] = {
        "a": 1,
        "c": {
            "e": {
                "f": "2"
            }
        }
    }

    provider = create_document_value_provider(doc)
    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(ancestor_names))


@pytest.mark.parametrize("create_document_value_provider", [DocumentValueProvider, TraceDocumentValueProvider])
def test_empty_doc(create_document_value_provider):
    doc: Dict[str, Any] = {}

    provider = create_document_value_provider(doc)

    with pytest.raises(KeyError):
        _ = provider.value(["a"])

    with pytest.raises(SourceNotFoundException):
        _ = provider.variable_value(create_variable(["b"]))
