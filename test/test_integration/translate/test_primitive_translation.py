from typing import Dict, Any

import pytest

from etl4.ontology.track import Track
from etl4.ontology.variable import Variable
from etl4.translate import Translate

@pytest.fixture
def track(single_primitive_target_stage) -> Track:
    return single_primitive_target_stage.track(True, True)

@pytest.fixture
def var(track) -> Variable:
    return track.from_id("target_var_id")

@pytest.fixture
def translate(track) -> Translate:
    return Translate.build(track)

def test_translate_no_sources_listed(translate, var, single_primitive_source_doc):
    """If a primitive is supposed to be translated but it has no sources, it is always null."""
    var.sources = []
    actual: Dict[str, Any] = translate(single_primitive_source_doc)
    expected: Dict[str, Any] = {
        "the_target": None
    }
    assert actual == expected

def test_translate_neither_source_has_values(translate):
    """If a primitive has sources but none have a value, it is null."""
    empty_doc: Dict = {}
    actual: Dict[str, Any] = translate(empty_doc)
    expected: Dict[str, Any] = {
        "the_target": None
    }
    assert actual == expected

def test_translate_first_source_has_value(translate, single_primitive_source_doc):
    """If a primitive has two sources and the first one has a value, that value is captured. Also tests casting
    behavior."""
    del single_primitive_source_doc["second_source"]
    actual: Dict[str, Any] = translate(single_primitive_source_doc)
    expected: Dict[str, Any] = {
        "the_target": 75
    }
    assert actual == expected

def test_translate_second_source_has_value(translate, single_primitive_source_doc):
    """If a primitive has two sources and only the second one has a value, that value is captured."""
    del single_primitive_source_doc["first_source"]
    actual: Dict[str, Any] = translate(single_primitive_source_doc)
    expected: Dict[str, Any] = {
        "the_target": 102
    }
    assert actual == expected

def test_translate_both_sources_have_values(translate, single_primitive_source_doc):
    """If a primitive has multiple sources and more than one has a value, the first source with a value is used. (This
    implies that source order matters.)"""
    actual: Dict[str, Any] = translate(single_primitive_source_doc)
    expected: Dict[str, Any] = {
        "the_target": 75
    }
    assert actual == expected
