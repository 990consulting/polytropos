from collections import OrderedDict
import pytest
from typing import Dict, Tuple, Any

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator

@pytest.fixture
def source() -> Tuple[Dict, Dict]:
    source_doc: Dict = {
        "outer_list_1": [
            {
                "inner_list": [
                    {"name": "inner_1_1_1"},
                    {"name": "inner_1_1_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_1_2_1"},
                    {"name": "inner_1_2_2"}
                ]
            }
        ],
        "outer_list_2": [
            {
                "inner_list": [
                    {"name": "inner_2_1_1"},
                    {"name": "inner_2_1_2"}
                ]
            },
            {
                "inner_list": [
                    {"name": "inner_2_2_1"},
                    {"name": "inner_2_2_2"}
                ]
            }
        ]
    }
    source_spec: Dict = {
        "outer_list_1_id": {
            "name": "outer_list_1",
            "data_type": "List",
            "sort_order": 0
        },
        "inner_list_1_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_1_id",
            "sort_order": 0
        },
        "name_1_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_1_id",
            "sort_order": 0
        },
        "outer_list_2_id": {
            "name": "outer_list_2",
            "data_type": "List",
            "sort_order": 1
        },
        "inner_list_2_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_2_id",
            "sort_order": 0
        },
        "name_2_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_2_id",
            "sort_order": 0
        }
    }

    return source_spec, source_doc

@pytest.fixture
def target() -> Tuple[Dict, Tuple["OrderedDict[str, Any]", "OrderedDict[str, Any]"]]:
    translate_doc: OrderedDict[str, Any] = OrderedDict([
        ("outer_list", [
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "inner_1_1_1")]),
                    OrderedDict([("name", "inner_1_1_2")]),
                ])
            ]),
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "inner_1_2_1")]),
                    OrderedDict([("name", "inner_1_2_2")]),
                ])
            ]),
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "inner_2_1_1")]),
                    OrderedDict([("name", "inner_2_1_2")]),
                ])
            ]),
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "inner_2_2_1")]),
                    OrderedDict([("name", "inner_2_2_2")]),
                ])
            ])
        ])
    ])

    trace_doc: OrderedDict[str, Any] = OrderedDict([
        ("outer_list", [
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "name_1_id")]),
                    OrderedDict([("name", "name_1_id")]),
                ])
            ]),
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "name_1_id")]),
                    OrderedDict([("name", "name_1_id")]),
                ])
            ]),
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "name_2_id")]),
                    OrderedDict([("name", "name_2_id")]),
                ])
            ]),
            OrderedDict([
                ("inner_list", [
                    OrderedDict([("name", "name_2_id")]),
                    OrderedDict([("name", "name_2_id")]),
                ])
            ])
        ])
    ])

    target_spec: Dict = {
        "outer_list_id": {
            "name": "outer_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["outer_list_1_id", "outer_list_2_id"]
        },
        "inner_list_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_id",
            "sort_order": 0,
            "sources": ["inner_list_1_id", "inner_list_2_id"]
        },
        "name_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_id",
            "sort_order": 0,
            "sources": ["name_1_id", "name_2_id"]
        }
    }

    return target_spec, (translate_doc, trace_doc)


@pytest.mark.parametrize(
    "index, create_document_value_provider", enumerate([DocumentValueProvider, TraceDocumentValueProvider])
)
def test_nested_list(source, target, index, create_document_value_provider):
    """Reversing the order of the sources in the target list spec results in an equivalent change in the order of the
    resulting list."""
    source_spec, source_doc = source
    target_spec, target_doc = target
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == target_doc[index]
