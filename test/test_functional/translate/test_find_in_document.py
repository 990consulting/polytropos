import pytest
from typing import Dict, Callable

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate.__translator import Translator, SourceNotFoundException

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "my_folder": {
            "day": "Tuesday",
            "the_folder": {
                "name": "Steve",
                "color": "orange"
            }
        },
        "meaning_of_life": 42,
        "root": {"nested": {"deeper": "nothing"}}
    }


@pytest.fixture()
def source_spec() -> Dict:
    return {
        "source_folder": {
            "name": "my_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_folder_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "parent": "source_folder",
            "sort_order": 0
        },
        "source_folder_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_folder_folder",
            "sort_order": 0
        },
        "source_folder_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_folder_folder",
            "sort_order": 1
        },
        "source_meaning_of_life": {
            "name": "meaning_of_life",
            "data_type": "Integer",
            "sort_order": 1
        },
        "source_root": {
            "name": "root",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_nested": {
            "name": "nested",
            "data_type": "Folder",
            "parent": "source_root",
            "sort_order": 0
        },
        "source_deeper": {
            "name": "deeper",
            "data_type": "Text",
            "parent": "source_nested",
            "sort_order": 0
        }
    }


@pytest.fixture()
def target_spec() -> Dict:
    return {}


@pytest.fixture()
def create_translator(source_spec: Dict, target_spec: Dict) -> Callable:
    def _create_translator(create_document_value_provider: Callable):
        source_track: Track = Track.build(source_spec, None, "Source")
        target_track: Track = Track.build(target_spec, source_track, "Target")
        return Translator(target_track, create_document_value_provider)
    return _create_translator


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, 42),
        (TraceDocumentValueProvider, "source_meaning_of_life"),
    ]
)
def test_base(source_doc, create_translator, create_document_value_provider, expected):
    translate = create_translator(create_document_value_provider)
    actual = create_document_value_provider(source_doc).variable_value(translate.source['source_meaning_of_life'])
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, ['nothing', 'orange']),
        (TraceDocumentValueProvider, ['source_deeper', 'source_folder_color']),
    ]
)
def test_deep(source_doc, create_translator, create_document_value_provider, expected):
    translate = create_translator(create_document_value_provider)
    actual = create_document_value_provider(source_doc).variable_value(translate.source['source_deeper'])
    assert actual == expected[0]
    actual = create_document_value_provider(source_doc).variable_value(translate.source['source_folder_color'])
    assert actual == expected[1]


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, 'orange'),
        (TraceDocumentValueProvider, 'source_folder_color'),
    ]
)
def test_parent(source_doc, create_translator, create_document_value_provider, expected):
    translate = create_translator(create_document_value_provider)
    actual = create_document_value_provider(source_doc['my_folder']).variable_value(translate.source['source_folder_color'], 'source_folder')
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider", [DocumentValueProvider, TraceDocumentValueProvider]
)
def test_parent_no_parent(source_doc, create_translator, create_document_value_provider):
    translate = create_translator(create_document_value_provider)
    with pytest.raises(SourceNotFoundException):
        create_document_value_provider(source_doc['my_folder']).variable_value(translate.source['source_folder_color'])


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, 'orange'),
        (TraceDocumentValueProvider, 'source_folder_color'),
    ]
)
def test_parent_immediate(source_doc, create_translator, create_document_value_provider, expected):
    translate = create_translator(create_document_value_provider)
    actual = create_document_value_provider(source_doc['my_folder']['the_folder']).variable_value(translate.source['source_folder_color'], 'source_folder_folder')
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider", [DocumentValueProvider, TraceDocumentValueProvider]
)
def test_parent_immediate_no_parent(source_doc, create_translator, create_document_value_provider):
    translate = create_translator(create_document_value_provider)
    with pytest.raises(SourceNotFoundException):
        create_document_value_provider(source_doc['my_folder']['the_folder']).variable_value(translate.source['source_folder_color'])
