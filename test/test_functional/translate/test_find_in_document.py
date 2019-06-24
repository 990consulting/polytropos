import pytest
from typing import Dict
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
def translate(source_spec: Dict, target_spec: Dict) -> Translator:
    source_track: Track = Track.build(source_spec, None, "Source")
    target_track: Track = Track.build(target_spec, source_track, "Target")
    translate: Translator = Translator(target_track)
    return translate


def test_base(source_doc, translate):
    actual = translate.find_in_document('source_meaning_of_life', source_doc)
    expected = 42
    assert actual == expected


def test_deep(source_doc, translate):
    actual = translate.find_in_document('source_deeper', source_doc)
    expected = 'nothing'
    assert actual == expected
    actual = translate.find_in_document('source_folder_color', source_doc)
    expected = 'orange'
    assert actual == expected


def test_parent(source_doc, translate):
    actual = translate.find_in_document(
        'source_folder_color', source_doc['my_folder'], 'source_folder'
    )
    expected = 'orange'
    assert actual == expected


def test_parent_no_parent(source_doc, translate):
    with pytest.raises(SourceNotFoundException):
        translate.find_in_document('source_folder_color', source_doc['my_folder'])


def test_parent_immediate(source_doc, translate):
    actual = translate.find_in_document(
        'source_folder_color', source_doc['my_folder']['the_folder'], 'source_folder_folder'
    )
    expected = 'orange'
    assert actual == expected


def test_parent_immediate_no_parent(source_doc, translate):
    with pytest.raises(SourceNotFoundException):
        actual = translate.find_in_document('source_folder_color', source_doc['my_folder']['the_folder'])
