import pytest
from typing import Dict
from addict import Dict as Addict
from etl4.ontology.track import Track
from etl4.translate import Translate

@pytest.fixture()
def source_doc() -> Addict:
    return Addict({
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
    })

@pytest.fixture()
def source_spec() -> Dict:
    return {
        "source_root_1": {
            "name": "list_source_1",
            "data_type": "NamedList",
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
            "data_type": "NamedList",
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
def target_spec() -> Addict:
    return Addict({
        "target_root": {
            "name": "People",
            "data_type": "NamedList",
            "sources": ["source_root_1", "source_root_2"],
            "sort_order": 0,
            "source_child_mappings": {
                "source_root_1": {
                    "target_root_name": ["source_root_1_name"],
                    "target_root_age": ["source_root_1_age"],
                    "target_root_ice_cream": ["source_root_1_ice_cream"],
                    "target_root_sport": ["source_root_1_sport"]
                },
                "source_root_2": {
                    "target_root_name": ["source_root_2_nombre"],
                    "target_root_age": ["source_root_2_edad"],
                    "target_root_ice_cream": ["source_root_2_helado"],
                    "target_root_sport": []
                }
            }
        },
        "target_root_name": {
            "name": "Name",
            "data_type": "Text",
            "sort_order": 0,
            "parent": "target_root"
        },
        "target_root_age": {
            "name": "Age",
            "data_type": "Integer",
            "sort_order": 1,
            "parent": "target_root"
        },
        "target_root_ice_cream": {
            "name": "Ice cream",
            "data_type": "Text",
            "sort_order": 2,
            "parent": "target_root"
        },
        "target_root_sport": {
            "name": "Sport",
            "data_type": "Text",
            "sort_order": 3,
            "parent": "target_root"
        }
    })

# TODO Used in multiple files -- should be a pytest.fixture
def do_test(s_doc, s_spec, t_doc, t_spec):
    source_track: Track = Track.build(s_spec)
    target_track: Track = Track.build(t_spec)
    translate: Translate = Translate(source_track, target_track)
    actual: Dict = translate(s_doc)
    assert actual == t_doc

def test_no_sources(source_doc: Addict, source_spec: Dict, target_spec: Addict):
    """No sources defined; empty dict is returned."""
    target_spec.source_child_mappings = {}
    target_spec.sources = []
    expected: Dict = {
        "People": {}
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_two_sources_both_missing(source_spec: Dict, target_spec: Addict):
    """Two sources defined, but both are missing from the source document; empty dict is returned."""
    source_doc = {}
    expected: Dict = {
        "People": {}
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_two_sources_both_empty(source_spec: Dict, target_spec: Addict):
    """Two sources defined, and both are present but empty; empty dict is returned."""
    source_doc = {
        "list_source_1": {},
        "list_source_2": {}
    }
    expected: Dict = {
        "People": {}
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_one_source(source_doc: Addict, source_spec: Dict, target_spec: Addict):
    """One source is specified; a target list is made from that source."""
    del target_spec.target_root.source_child_mappings.source_root_1
    target_spec.sources = ["source_root_2"]
    expected: Dict = {
        "People": {
            "Stacy": {
                "Age": 26,
                "Ice cream": "chocolate",
                "Sport": None
            }
        }
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_two_sources_one_empty(source_doc: Addict, source_spec: Dict, target_spec: Addict):
    """Two sources are defined, but one is empty."""
    source_doc.list_source_1 = []
    expected: Dict = {
        "People": {
            "Stacy": {
                "Name": "Stacy",
                "Age": 26,
                "Ice cream": "chocolate",
                "Sport": None
            }
        }
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_combine_lists(source_doc, source_spec, target_spec):
    """Verify that, when two sources both have items, they get combined into one list."""
    expected: Dict = {
        "People": {
            "Steve": {
                "Name": "Steve",
                "Age": 32,
                "Ice cream": "strawberry",
                "Sport": "tennis"
            },
            "Hannah": {
                "Name": "Hannah",
                "Age": None,
                "Ice cream": "rocky road",
                "Sport": None
            },
            "Stacy": {
                "Name": "Stacy",
                "Age": 26,
                "Ice cream": "chocolate",
                "Sport": None
            }
        }
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_source_order_matters(source_doc, source_spec, target_spec):
    """Reversing the order of the sources in the target list spec results in an equivalent change in the order of the
    resulting list."""
    target_spec.target_root.sources = ["source_root_2", "source_root_1"]
    expected: Dict = {
        "People": {
            "Stacy": {
                "Name": "Stacy",
                "Age": 26,
                "Ice cream": "chocolate",
                "Sport": None
            },
            "Steve": {
                "Name": "Steve",
                "Age": 32,
                "Ice cream": "strawberry",
                "Sport": "tennis"
            },
            "Hannah": {
                "Name": "Hannah",
                "Age": None,
                "Ice cream": "rocky road",
                "Sport": None
            }
        }
    }
    do_test(source_doc, source_spec, expected, target_spec)

def test_duplicate_name_raises(source_doc, source_spec, target_spec):
    source_doc.list_source_1.Stacy = {
        "Name": "Another Stacy"
    }
    with pytest.raises(ValueError):
        do_test(source_doc, source_spec, {}, target_spec)
