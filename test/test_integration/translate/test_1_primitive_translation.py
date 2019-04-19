from typing import Dict, Any, Iterable

import pytest

from etl4.ontology.track import Track
from etl4.translate import Translate

@pytest.fixture()
def source_1_spec() -> Dict:
    return {
        "_id": "source_var_1",
        "name": "first_source",
        "data_type": "Integer"
    }

@pytest.fixture()
def source_2_spec() -> Dict:
    return {
        "_id": "source_var_2",
        "name": "second_source",
        "data_type": "Integer"
    }

@pytest.fixture()
def source_specs(source_1_spec, source_2_spec) -> Iterable[Dict]:
    return [source_1_spec, source_2_spec]

@pytest.fixture()
def target_spec() -> Dict:
    return {
        "_id": "target_var_id",
        "name": "the_target",
        "data_type": "Integer",
        "sources": ["source_var_1", "source_var_2"]
    }

@pytest.fixture()
def translate(source_specs: Iterable[Dict], target_spec: Dict) -> Translate:
    source_track: Track = Track.build(source_specs)
    target_track: Track = Track.build([target_spec])
    translate: Translate = Translate(source_track, target_track)
    return translate

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "first_source": 75,
        "second_source": 102
    }

def test_translate_no_sources_listed(target_spec: Dict, source_specs: Iterable[Dict], source_doc: Dict):
    """If a primitive is supposed to be translated but it has no sources, it is always null."""
    source_track: Track = Track.build(source_specs)

    target_spec["sources"] = []
    target_track: Track = Track.build([target_spec])

    translate: Translate = Translate(source_track, target_track)

    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": None
    }
    assert actual == expected

def test_translate_neither_source_has_values(translate: Translate):
    """If a primitive has sources but none have a value, it is null."""
    empty_doc: Dict = {}
    actual: Dict[str, Any] = translate(empty_doc)
    expected: Dict[str, Any] = {
        "the_target": None
    }
    assert actual == expected

def test_translate_first_source_has_value(translate: Translate, source_doc: Dict):
    """If a primitive has two sources and the first one has a value, that value is captured."""
    del source_doc["second_source"]
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 75
    }
    assert actual == expected

def test_translate_second_source_has_value(translate: Translate, source_doc: Dict):
    """If a primitive has two sources and the second one has a value, that value is captured."""
    del source_doc["first_source"]
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 102
    }
    assert actual == expected

def test_translate_both_sources_have_values(translate: Translate, source_doc: Dict):
    """If a primitive has multiple sources and more than one has a value, the first source with a value is used. (This
    implies that source order matters.)"""
    actual: Dict[str, Any] = translate(source_doc)
    expected: Dict[str, Any] = {
        "the_target": 75
    }
    assert actual == expected
