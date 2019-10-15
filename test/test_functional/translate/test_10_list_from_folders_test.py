from collections import OrderedDict
import pytest
from typing import Dict, Tuple, Any

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator

@pytest.fixture()
def source() -> Tuple[Dict, Dict]:
    doc: Dict = {
        "first_source_folder": {
            "name": "Steve",
            "color": "red"
        },
        "second_source_folder": {
            "name": "Bob",
            "color": "blue"
        }

    }

    spec: Dict = {
        "source_folder_1": {
            "name": "first_source_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_name_1": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_folder_1",
            "sort_order": 0
        },
        "source_color_1": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_folder_1",
            "sort_order": 1
        },
        "source_folder_2": {
            "name": "second_source_folder",
            "data_type": "Folder",
            "sort_order": 1
        },
        "source_name_2": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_folder_2",
            "sort_order": 0
        },
        "source_color_2": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_folder_2",
            "sort_order": 1
        },

    }
    return spec, doc

@pytest.fixture
def target() -> Tuple[Dict, Tuple["OrderedDict[str, Any]", "OrderedDict[str, Any]"]]:
    translate_doc: OrderedDict[str, Any] = OrderedDict([
        ("the_list", [
            OrderedDict([
                ("name", "Steve"),
                ("color", "red")
            ]),
            OrderedDict([
                ("name", "Bob"),
                ("color", "blue")
            ])
        ])
    ])

    trace_doc: OrderedDict[str, Any] = OrderedDict([
        ("the_list", [
            OrderedDict([
                ("name", "source_name_1"),
                ("color", "source_color_1")
            ]),
            OrderedDict([
                ("name", "source_name_2"),
                ("color", "source_color_2")
            ])
        ])
    ])

    spec: Dict = {
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["source_folder_1", "source_folder_2"],
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0,
            "sources": ["source_name_1", "source_name_2"]
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 1,
            "sources": ["source_color_1", "source_color_2"]
        }
    }

    return spec, (translate_doc, trace_doc)


@pytest.mark.parametrize(
    "index, create_document_value_provider", enumerate([DocumentValueProvider, TraceDocumentValueProvider])
)
def test_list_from_folders(source, target, index, create_document_value_provider):
    source_spec, source_doc = source
    target_spec, expected = target
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected[index]


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_list", [
                OrderedDict([
                    ("name", "Steve"),
                    ("color", "red")
                ])
            ])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_list", [
                OrderedDict([
                    ("name", "source_name_1"),
                    ("color", "source_color_1")
                ])
            ])
        ]))]
)
def test_folder_null_skipped(source, target, create_document_value_provider, expected):
    """On occasion, e-files contain <EmptyElements/> that would normally contain list items. These are converted to
    JSON as {"EmptyElement": null} and are not included as list items during translation."""
    source_spec, source_doc = source
    source_doc["second_source_folder"] = None
    target_spec, _ = target
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected
