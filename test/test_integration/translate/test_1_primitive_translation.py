from typing import Any, Dict
import pytest

from polytropos.ontology.track import Track
from polytropos.actions.translate import Translator

@pytest.fixture()
def source_spec() -> Dict:
    return {
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
def translate(source_spec: Dict, target_spec: Dict) -> Translator:
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track)
    return translate

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "first_source": 75,
        "second_source": 102
    }

def test_translate_no_sources_listed(target_spec: Dict, source_spec: Dict, source_doc: Dict):
    """If a primitive is supposed to be translated but it has no sources, it is always null."""
    source_track: Track = Track.build(source_spec, None, "Source")

    target_spec["target_var_id"]["sources"] = []
    target_track: Track = Track.build(target_spec, source_track, "Target")

    translate: Translator = Translator(target_track)

    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": None
    }

    assert actual == expected

def test_translate_neither_source_has_values(translate: Translator):
    """If a primitive has sources but none have a value, it is null."""
    empty_doc: Dict = {}
    actual: Dict[str, Any] = translate(empty_doc)
    expected: Dict[str, Any] = {
        "the_target": None
    }
    assert actual == expected

def test_translate_first_source_has_value(translate: Translator, source_doc: Dict):
    """If a primitive has two sources and the first one has a value, that value is captured."""
    del source_doc["second_source"]
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 75
    }
    assert actual == expected

def test_translate_second_source_has_value(translate: Translator, source_doc: Dict):
    """If a primitive has two sources and the second one has a value, that value is captured."""
    del source_doc["first_source"]
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 102
    }
    assert actual == expected

def test_translate_none_means_skip(translate: Translator, source_doc: Dict):
    """If a source exists and has a null value, treat that as if it weren't there."""
    source_doc["first_source"] = None
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 102
    }
    assert actual == expected

def test_translate_both_sources_have_values(translate: Translator, source_doc: Dict):
    """If a primitive has multiple sources and more than one has a value, the first source with a value is used. (This
    implies that source order matters.)"""
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 75
    }
    assert actual == expected

def test_use_same_source_twice(source_spec: Dict, source_doc: Dict):
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
    translate: Translator = Translator(target_track)

    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "first_target": 75,
        "second_target": 75
    }

    assert actual == expected
