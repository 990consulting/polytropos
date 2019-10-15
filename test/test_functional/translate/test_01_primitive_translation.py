from collections import OrderedDict
from typing import Any, Dict, Callable
import pytest

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator


@pytest.fixture()
def source_spec() -> Dict:
    return {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "sort_order": 1
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "sort_order": 0
        }
    }


@pytest.fixture()
def target_spec() -> Dict:
    return {
        "target_var_id": {
            "name": "the_target",
            "data_type": "Integer",
            "sources": ["source_var_1", "source_var_2"],
            "sort_order": 0
        }
    }


@pytest.fixture()
def create_translator(source_spec: Dict, target_spec: Dict) -> Callable:
    def _create_translator(create_document_value_provider: Callable):
        source_track: Track = Track.build(source_spec, None, "Source")
        target_track: Track = Track.build(target_spec, source_track, "Target")
        return Translator(target_track, create_document_value_provider)
    return _create_translator


@pytest.fixture()
def source_doc() -> Dict:
    return {
        "first_source": 75,
        "second_source": 102
    }


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict()),
        (TraceDocumentValueProvider, OrderedDict()),
    ]
)
def test_translate_no_sources_listed(target_spec: Dict, source_spec: Dict, source_doc: Dict, create_document_value_provider, expected):
    """If a primitive is supposed to be translated but it has no sources, it is always null."""
    source_track: Track = Track.build(source_spec, None, "Source")

    target_spec["target_var_id"]["sources"] = []
    target_track: Track = Track.build(target_spec, source_track, "Target")

    translate: Translator = Translator(target_track, create_document_value_provider)

    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict()),
        (TraceDocumentValueProvider, OrderedDict()),
    ]
)
def test_translate_neither_source_has_values(create_translator, create_document_value_provider, expected):
    """If a primitive has sources but none have a value, it is not translated."""
    empty_doc: Dict = {}
    translate = create_translator(create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", empty_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_target", 75)
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_target", "source_var_1")
        ])),
    ]
)
def test_translate_first_source_has_value(source_doc: Dict, create_translator, create_document_value_provider, expected):
    """If a primitive has two sources and the first one has a value, that value is captured."""
    del source_doc["second_source"]
    translate = create_translator(create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_target", None)
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_target", "source_var_1")
        ])),
    ]
)
def test_source_has_null_value(create_translator, create_document_value_provider, expected):
    """If a variable's source has an explicit null value, the target is explicitly null."""
    doc: Dict = {
        "first_source": None
    }
    translate = create_translator(create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_target", None)
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_target", "source_var_1")
        ])),
    ]
)
def test_first_null_second_non_null(create_translator, create_document_value_provider, expected):
    """If a variable has 2+ sources and the first extant one is explicitly null, the target is explicitly null."""
    doc: Dict = {
        "first_source": None,
        "second_source": 5
    }
    translate = create_translator(create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_target", 102)
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_target", "source_var_2")
        ])),
    ]
)
def test_translate_second_source_has_value(source_doc: Dict, create_translator, create_document_value_provider, expected):
    """If a primitive has two sources and the second one has a value, that value is captured."""
    del source_doc["first_source"]
    translate = create_translator(create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_target", 75)
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_target", "source_var_1")
        ])),
    ]
)
def test_translate_both_sources_have_values(source_doc: Dict, create_translator, create_document_value_provider, expected):
    """If a primitive has multiple sources and more than one has a value, the first source with a value is used. (This
    implies that source order matters.)"""
    translate = create_translator(create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("first_target", 75),
            ("second_target", 75),
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("first_target", "source_var_1"),
            ("second_target", "source_var_1"),
        ])),
    ]
)
def test_use_same_source_twice(source_spec: Dict, source_doc: Dict, create_document_value_provider, expected):
    """Two targets can use the same source."""
    target_spec: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "sort_order": 1
        }
    }
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)

    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected
