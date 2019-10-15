from collections import OrderedDict

import pytest
from typing import Dict, Any

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator


@pytest.fixture()
def source_doc() -> Dict:
    return {
        "list_source_1": [
            {
                "name": "Steve",
                "nom": "Etienne",  # There are two sources for name in list_source_1; sources are checked in order.
                "age": 32,
                "ice cream": "strawberry",
                "sport": "tennis"
            },
            {
                "nom": "Hannah",
                "ice cream": "rocky road",
            }
        ],
        "list_source_2": [
            {
                "nombre": "Stacy",
                "edad": 26,
                "helado": "chocolate"
            }
        ]
    }


@pytest.fixture()
def source_spec() -> Dict:
    return {
        "source_root_1": {
            "name": "list_source_1",
            "data_type": "List",
            "sort_order": 0
        },
        "source_root_1_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 0
        },
        "source_root_1_nom": {
            "name": "nom",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 1
        },
        "source_root_1_age": {
            "name": "age",
            "data_type": "Integer",
            "parent": "source_root_1",
            "sort_order": 2
        },
        "source_root_1_ice_cream": {
            "name": "ice cream",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 3
        },
        "source_root_1_sport": {
            "name": "sport",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 4
        },
        "source_root_2": {
            "name": "list_source_2",
            "data_type": "List",
            "sort_order": 1,
        },
        "source_root_2_nombre": {
            "name": "nombre",
            "data_type": "Text",
            "parent": "source_root_2",
            "sort_order": 0
        },
        "source_root_2_edad": {
            "name": "edad",
            "data_type": "Integer",
            "parent": "source_root_2",
            "sort_order": 1
        },
        "source_root_2_helado": {
            "name": "helado",
            "data_type": "Text",
            "parent": "source_root_2",
            "sort_order": 2
        }
    }


@pytest.fixture()
def target_spec() -> Dict:
    return {
        "target_root": {
            "name": "People",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["source_root_1", "source_root_2"],
        },
        "target_root_name": {
            "name": "Name",
            "data_type": "Text",
            "sort_order": 0,
            "parent": "target_root",
            "sources": ["source_root_1_name", "source_root_1_nom", "source_root_2_nombre"]
        },
        "target_root_age": {
            "name": "Age",
            "data_type": "Integer",
            "sort_order": 1,
            "parent": "target_root",
            "sources": ["source_root_1_age", "source_root_2_edad"],
        },
        "target_root_ice_cream": {
            "name": "Ice cream",
            "data_type": "Text",
            "sort_order": 2,
            "parent": "target_root",
            "sources": ["source_root_1_ice_cream", "source_root_2_helado"],
        },
        "target_root_sport": {
            "name": "Sport",
            "data_type": "Text",
            "sort_order": 3,
            "parent": "target_root",
            "sources": ["source_root_1_sport"]
        }
    }


def do_test(s_doc, s_spec, t_doc, t_spec, create_document_value_provider):
    source_track: Track = Track.build(s_spec, None, "Source")
    target_track: Track = Track.build(t_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", s_doc)
    assert actual == t_doc


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict()),
        (TraceDocumentValueProvider, OrderedDict())
    ]
)
def test_no_sources(source_doc: Dict, source_spec: Dict, target_spec: Dict, create_document_value_provider, expected):
    """No sources defined; no list is created."""
    for key in target_spec.keys():
        target_spec[key]["sources"] = []

    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("People", [])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("People", [])
        ]))
    ]
)
def test_two_sources_both_missing(source_spec: Dict, target_spec: Dict, create_document_value_provider, expected):
    """Two sources defined, but both are missing from the source document; an empty list is created."""
    source_doc = {}
    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("People", [])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("People", [])
        ]))
    ]
)
def test_two_sources_both_empty(source_spec: Dict, target_spec: Dict, create_document_value_provider, expected):
    """Two sources defined, and both are present but empty; an empty list is created."""
    source_doc = {
        "list_source_1": [],
        "list_source_2": []
    }
    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "Stacy"),
                    ("Age", 26),
                    ("Ice cream", "chocolate")
                ])
            ])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "source_root_2_nombre"),
                    ("Age", "source_root_2_edad"),
                    ("Ice cream", "source_root_2_helado")
                ])
            ])
        ]))
    ]
)
def test_one_source(source_doc: Dict, source_spec: Dict, target_spec: Dict, create_document_value_provider, expected):
    """One source is specified; a target list is made from that source."""
    target_spec["target_root"]["sources"] = ["source_root_2"]
    target_spec["target_root_name"]["sources"] = ["source_root_2_nombre"]
    target_spec["target_root_age"]["sources"] = ["source_root_2_edad"]
    target_spec["target_root_ice_cream"]["sources"] = ["source_root_2_helado"]
    target_spec["target_root_sport"]["sources"] = []

    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "Stacy"),
                    ("Age", 26),
                    ("Ice cream", "chocolate")
                ])
            ])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "source_root_2_nombre"),
                    ("Age", "source_root_2_edad"),
                    ("Ice cream", "source_root_2_helado")
                ])
            ])
        ]))
    ]
)
def test_two_sources_one_empty(source_doc: Dict, source_spec: Dict, target_spec: Dict, create_document_value_provider, expected):
    """Two sources are defined, but one is empty."""
    source_doc["list_source_1"] = []
    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "Steve"),
                    ("Age", 32),
                    ("Ice cream", "strawberry"),
                    ("Sport", "tennis")
                ]),
                OrderedDict([
                    ("Name", "Hannah"),
                    ("Ice cream", "rocky road")
                ]),
                OrderedDict([
                    ("Name", "Stacy"),
                    ("Age", 26),
                    ("Ice cream", "chocolate")
                ])
            ])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "source_root_1_name"),
                    ("Age", "source_root_1_age"),
                    ("Ice cream", "source_root_1_ice_cream"),
                    ("Sport", "source_root_1_sport")
                ]),
                OrderedDict([
                    ("Name", "source_root_1_nom"),
                    ("Ice cream", "source_root_1_ice_cream")
                ]),
                OrderedDict([
                    ("Name", "source_root_2_nombre"),
                    ("Age", "source_root_2_edad"),
                    ("Ice cream", "source_root_2_helado")
                ])
            ])
        ]))
    ]
)
def test_combine_lists(source_doc, source_spec, target_spec, create_document_value_provider, expected):
    """Verify that, when two sources both have items, they get combined into one list. Remember that list source 1 has
    two name fields, which are checked in order (see test_1_primitive_translation.py)."""
    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "Stacy"),
                    ("Age", 26),
                    ("Ice cream", "chocolate")
                ]),
                OrderedDict([
                    ("Name", "Steve"),
                    ("Age", 32),
                    ("Ice cream", "strawberry"),
                    ("Sport", "tennis")
                ]),
                OrderedDict([
                    ("Name", "Hannah"),
                    ("Ice cream", "rocky road")
                ])
            ])
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("People", [
                OrderedDict([
                    ("Name", "source_root_2_nombre"),
                    ("Age", "source_root_2_edad"),
                    ("Ice cream", "source_root_2_helado")
                ]),
                OrderedDict([
                    ("Name", "source_root_1_name"),
                    ("Age", "source_root_1_age"),
                    ("Ice cream", "source_root_1_ice_cream"),
                    ("Sport", "source_root_1_sport")
                ]),
                OrderedDict([
                    ("Name", "source_root_1_nom"),
                    ("Ice cream", "source_root_1_ice_cream")
                ])
            ])
        ]))]
)
def test_source_order_matters(source_doc, source_spec, target_spec, create_document_value_provider, expected):
    """Reversing the order of the sources in the target list spec results in an equivalent change in the order of the
    resulting list."""
    target_spec["target_root"]["sources"] = ["source_root_2", "source_root_1"]
    do_test(source_doc, source_spec, expected, target_spec, create_document_value_provider)
