"""Test methods that encode and decode lists. These methods do not actually care about the content of the composite
itself, but only its schema; they take content as an argument and return the same content in a different
representation."""
from collections import OrderedDict

import pytest
from typing import Dict, Any
from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "list_source_1": {
            "Steve": {
                "name": "Steve",
                "age": 32,
                "ice cream": "strawberry",
                "sport": "tennis"
            },
            "Hannah": {
                "name": "Hannah",
                "ice cream": "rocky road",
            }
        },
        "list_source_2": {
            "Stacy": {
                "nombre": "Stacy",
                "edad": 26,
                "helado": "chocolate"
            }
        }
    }

@pytest.fixture()
def source_spec() -> Dict:
    return {
        "source_root_1": {
            "name": "list_source_1",
            "data_type": "KeyedList",
            "sort_order": 0
        },
        "source_root_1_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 0
        },
        "source_root_1_age": {
            "name": "age",
            "data_type": "Integer",
            "parent": "source_root_1",
            "sort_order": 1
        },
        "source_root_1_ice_cream": {
            "name": "ice cream",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 2
        },
        "source_root_1_sport": {
            "name": "sport",
            "data_type": "Text",
            "parent": "source_root_1",
            "sort_order": 3
        },
        "source_root_2": {
            "name": "list_source_2",
            "data_type": "KeyedList",
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
            "data_type": "KeyedList",
            "sources": ["source_root_1", "source_root_2"],
            "sort_order": 0,
        },
        "target_root_name": {
            "name": "Name",
            "data_type": "Text",
            "sort_order": 0,
            "parent": "target_root",
            "sources": ["source_root_1_name", "source_root_2_nombre"]
        },
        "target_root_age": {
            "name": "Age",
            "data_type": "Integer",
            "sort_order": 1,
            "parent": "target_root",
            "sources": ["source_root_1_age", "source_root_2_edad"]
        },
        "target_root_ice_cream": {
            "name": "Ice cream",
            "data_type": "Text",
            "sort_order": 2,
            "parent": "target_root",
            "sources": ["source_root_1_ice_cream", "source_root_2_helado"]
        },
        "target_root_sport": {
            "name": "Sport",
            "data_type": "Text",
            "sort_order": 3,
            "parent": "target_root",
            "sources": ["source_root_1_sport"]
        }
    }

# TODO Used in multiple files -- should be a pytest.fixture
def do_test(s_doc, s_spec, t_doc, t_spec):
    source_track: Track = Track.build(s_spec, None, "Source")
    target_track: Track = Track.build(t_spec, source_track, "Target")
    translate: Translator = Translator(target_track)
    actual: OrderedDict[str, Any] = translate("composite_id", "period", s_doc)
    assert actual == t_doc

def test_no_sources(source_doc: Dict, source_spec: Dict, target_spec: Dict):
    """No sources defined; empty dict is returned."""
    target_spec["target_root"]["sources"] = []
    target_spec["target_root_name"]["sources"] = []
    target_spec["target_root_age"]["sources"] = []
    target_spec["target_root_ice_cream"]["sources"] = []
    target_spec["target_root_sport"]["sources"] = []
    expected: OrderedDict[str, Any] = OrderedDict()
    do_test(source_doc, source_spec, expected, target_spec)

def test_two_sources_both_missing(source_spec: Dict, target_spec: Dict):
    """Two sources defined, but both are missing from the source document; empty dict is returned."""
    source_doc = {}
    expected: OrderedDict[str, Any] = OrderedDict()
    do_test(source_doc, source_spec, expected, target_spec)

def test_two_sources_both_empty(source_spec: Dict, target_spec: Dict):
    """Two sources defined, and both are present but empty; empty dict is returned."""
    source_doc = {
        "list_source_1": {},
        "list_source_2": {}
    }
    expected: OrderedDict[str, Any] = OrderedDict([
        ("People", OrderedDict())
    ])
    do_test(source_doc, source_spec, expected, target_spec)

def test_one_source(source_doc: Dict, source_spec: Dict, target_spec: Dict):
    """One source is specified; a target list is made from that source."""
    target_spec["target_root"]["sources"] = ["source_root_2"]
    target_spec["target_root_name"]["sources"] = ["source_root_2_nombre"]
    target_spec["target_root_age"]["sources"] = ["source_root_2_edad"]
    target_spec["target_root_ice_cream"]["sources"] = ["source_root_2_helado"]
    target_spec["target_root_sport"]["sources"] = []
    expected: OrderedDict[str, Any] = OrderedDict([
        ("People", OrderedDict([
            ("Stacy", OrderedDict([
                ("Name", "Stacy"),
                ("Age", 26),
                ("Ice cream", "chocolate")
            ]))
        ]))
    ])
    do_test(source_doc, source_spec, expected, target_spec)

def test_two_sources_one_empty(source_doc: Dict, source_spec: Dict, target_spec: Dict):
    """Two sources are defined, but one is empty."""
    source_doc["list_source_1"] = {}
    expected: OrderedDict[str, Any] = OrderedDict([
        ("People", OrderedDict([
            ("Stacy", OrderedDict([
                ("Name", "Stacy"),
                ("Age", 26),
                ("Ice cream", "chocolate")
            ]))
        ]))
    ])
    do_test(source_doc, source_spec, expected, target_spec)

def test_combine_lists(source_doc, source_spec, target_spec):
    """Verify that, when two sources both have items, they get combined into one list."""
    expected: OrderedDict[str, Any] = OrderedDict([
        ("People", OrderedDict([
            ("Steve", OrderedDict([
                ("Name", "Steve"),
                ("Age", 32),
                ("Ice cream", "strawberry"),
                ("Sport", "tennis")
            ])),
            ("Hannah", OrderedDict([
                ("Name", "Hannah"),
                ("Ice cream", "rocky road")
            ])),
            ("Stacy", OrderedDict([
                ("Name", "Stacy"),
                ("Age", 26),
                ("Ice cream", "chocolate")
            ]))
        ]))
    ])
    do_test(source_doc, source_spec, expected, target_spec)

def test_source_order_matters(source_doc, source_spec, target_spec):
    """Reversing the order of the sources in the target list spec results in an equivalent change in the order of the
    resulting list."""
    target_spec["target_root"]["sources"] = ["source_root_2", "source_root_1"]
    expected: OrderedDict[str, Any] = OrderedDict([
        ("People", OrderedDict([
            ("Stacy", OrderedDict([
                ("Name", "Stacy"),
                ("Age", 26),
                ("Ice cream", "chocolate")
            ])),
            ("Steve", OrderedDict([
                ("Name", "Steve"),
                ("Age", 32),
                ("Ice cream", "strawberry"),
                ("Sport", "tennis")
            ])),
            ("Hannah", OrderedDict([
                ("Name", "Hannah"),
                ("Ice cream", "rocky road")
            ])),
        ]))
    ])
    do_test(source_doc, source_spec, expected, target_spec)

def test_duplicate_name_raises(source_doc, source_spec, target_spec):
    source_doc["list_source_1"]["Stacy"] = {
        "Name": "Another Stacy"
    }
    with pytest.raises(ValueError):
        source_track: Track = Track.build(source_spec, None, "Source")
        target_track: Track = Track.build(target_spec, source_track, "Target")
        translate: Translator = Translator(target_track)
        translate("composite_id", "period", source_doc)

