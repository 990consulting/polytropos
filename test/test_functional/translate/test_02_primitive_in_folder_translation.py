from collections import OrderedDict
import pytest
from typing import Dict, Tuple, Callable, Iterable, Any
import itertools

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator


def source_flat() -> Tuple[Dict, Dict]:
    source: Dict = {
        "first_source": 75,
        "second_source": 102
    }

    spec: Dict = {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "sort_order": 0
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "sort_order": 1
        }
    }
    return source, spec


def source_one_folder() -> Tuple[Dict, Dict]:
    source: Dict = {
        "the_folder": {
            "first_source": 75,
            "second_source": 102
        }
    }

    spec: Dict = {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder",
            "sort_order": 0
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder",
            "sort_order": 1
        },
        "source_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "sort_order": 0
        }
    }

    return source, spec


def source_two_folders() -> Tuple[Dict, Dict]:
    source: Dict = {
        "first_folder": {
            "first_source": 75
        },
        "second_folder": {
            "second_source": 102,
        }
    }

    spec: Dict = {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder_1",
            "sort_order": 0
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder_2",
            "sort_order": 0
        },
        "source_folder_1": {
            "name": "first_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_folder_2": {
            "name": "second_folder",
            "data_type": "Folder",
            "sort_order": 1
        }
    }
    return source, spec


def source_nested() -> Tuple[Dict, Dict]:
    source: Dict = {
        "outer_s": {
            "first_source": 75,
            "inner_s": {
                "second_source": 102,
            }
        }
    }

    spec: Dict = {
        "source_var_1": {
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder_1",
            "sort_order": 0
        },
        "source_var_2": {
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder_2",
            "sort_order": 0
        },
        "source_folder_1": {
            "name": "outer_s",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_folder_2": {
            "name": "inner_s",
            "data_type": "Folder",
            "parent": "source_folder_1",
            "sort_order": 1
        }
    }

    return source, spec


def target_flat() -> Tuple[Tuple["OrderedDict[str, Any]", "OrderedDict[str, Any]"], Dict]:
    translate_target: OrderedDict[str, Any] = OrderedDict([
        ("first_target", 75),
        ("second_target", 102)
    ])

    trace_target: OrderedDict[str, Any] = OrderedDict([
        ("first_target", "source_var_1"),
        ("second_target", "source_var_2")
    ])

    spec: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "sort_order": 0,
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "sources": ["source_var_2"],
            "sort_order": 1
        }
    }
    return (translate_target, trace_target), spec


def target_one_folder() -> Tuple[Tuple["OrderedDict[str, Any]", "OrderedDict[str, Any]"], Dict]:
    translate_target: OrderedDict[str, Any] = OrderedDict([
        ("the_folder", OrderedDict([
            ("first_target", 75),
            ("second_target", 102)
        ]))
    ])

    trace_target: OrderedDict[str, Any] = OrderedDict([
        ("the_folder", OrderedDict([
            ("first_target", "source_var_1"),
            ("second_target", "source_var_2")
        ]))
    ])

    spec: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder",
            "sources": ["source_var_1"],
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder",
            "sources": ["source_var_2"],
            "sort_order": 1
        },
        "target_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "sort_order": 0
        }
    }
    return (translate_target, trace_target), spec


def target_two_folders() -> Tuple[Tuple["OrderedDict[str, Any]", "OrderedDict[str, Any]"], Dict]:
    translate_target: OrderedDict[str, Any] = OrderedDict([
        ("first_folder", OrderedDict([
            ("first_target", 75)
        ])),
        ("second_folder", OrderedDict([
            ("second_target", 102),
        ]))
    ])

    trace_target: OrderedDict[str, Any] = OrderedDict([
        ("first_folder", OrderedDict([
            ("first_target", "source_var_1")
        ])),
        ("second_folder", OrderedDict([
            ("second_target", "source_var_2"),
        ]))
    ])

    spec: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "parent": "target_folder_1",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "sources": ["source_var_2"],
            "parent": "target_folder_2",
            "sort_order": 0
        },
        "target_folder_1": {
            "name": "first_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_folder_2": {
            "name": "second_folder",
            "data_type": "Folder",
            "sort_order": 1
        }
    }
    return (translate_target, trace_target), spec


def target_nested() -> Tuple[Tuple["OrderedDict[str, Any]", "OrderedDict[str, Any]"], Dict]:
    translate_target: OrderedDict[str, Any] = OrderedDict([
        ("outer_s", OrderedDict([
            ("first_target", 75),
            ("inner_s", OrderedDict([
                ("second_target", 102),
            ]))
        ]))
    ])

    trace_target: OrderedDict[str, Any] = OrderedDict([
        ("outer_s", OrderedDict([
            ("first_target", "source_var_1"),
            ("inner_s", OrderedDict([
                ("second_target", "source_var_2"),
            ]))
        ]))
    ])

    spec: Dict = {
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sources": ["source_var_1"],
            "parent": "target_folder_1",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "sources": ["source_var_2"],
            "parent": "target_folder_2",
            "sort_order": 0
        },
        "target_folder_1": {
            "name": "outer_s",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_folder_2": {
            "name": "inner_s",
            "data_type": "Folder",
            "parent": "target_folder_1",
            "sort_order": 1
        }
    }
    return (translate_target, trace_target), spec


sources: Iterable = [source_flat, source_one_folder, source_two_folders, source_nested]
targets: Iterable = [target_flat, target_one_folder, target_two_folders, target_nested]

@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict()),
        (TraceDocumentValueProvider, OrderedDict()),
    ]
)
@pytest.mark.parametrize("source, target", itertools.product(sources, targets))
def test_translate_all_children_missing(source: Callable, target: Callable, create_document_value_provider, expected):
    __, source_spec = source()
    __, target_spec = target()
    source_doc: Dict = {}
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "create_document_value_provider, expected", [
        (DocumentValueProvider, OrderedDict([
            ("the_folder", OrderedDict([
                ("first_target", None),
                ("second_target", None)
            ]))
        ])),
        (TraceDocumentValueProvider, OrderedDict([
            ("the_folder", OrderedDict([
                ("first_target", "source_var_1"),
                ("second_target", "source_var_2")
            ]))
        ])),
    ]
)
def test_translate_all_children_none(create_document_value_provider, expected):
    __, source_spec = source_one_folder()
    __, target_spec = target_one_folder()
    source_doc: Dict = {
        "the_folder": {
            "first_source": None,
            "second_source": None
        }
    }
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected


@pytest.mark.parametrize(
    "index, create_document_value_provider", enumerate([DocumentValueProvider, TraceDocumentValueProvider])
)
@pytest.mark.parametrize("source, target", itertools.product(sources, targets))
def test_translate_with_folders(source: Callable, target: Callable, index, create_document_value_provider):
    """Summary: verify that source topology doesn't matter for a given target spec.

    Long version: Try every combination of the above examples. Because a target variable's source is defined by ID,
    the particular location of the source variable in the source hierarchy is irrelevant. That is, no matter how the
    source hierarchy is arranged, a target spec should produce the same target hierarchy as long as all the source
    variables exist."""
    source_doc, source_spec = source()
    expected, target_spec = target()
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track, create_document_value_provider)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", source_doc)
    assert actual == expected[index]
