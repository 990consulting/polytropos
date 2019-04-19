import pytest
from addict import Dict as Addict
from typing import Dict, Iterable

from etl4.ontology.track import Track
from etl4.translate import Translate

@pytest.fixture()
def source_doc_flat() -> Addict:
    return Addict({
        "first_source": 75,
        "second_source": 102
    })

@pytest.fixture()
def source_spec_flat() -> Addict:
    return Addict({
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
    })

@pytest.fixture()
def source_doc_one_folder() -> Addict:
    return Addict({
        "the_folder": {
            "first_source": 75,
            "second_source": 102
        }
    })

@pytest.fixture()
def source_spec_one_folder() -> Addict:
    return Addict({
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
            "data_type": "folder",
            "sort_order": 0
        }
    })

@pytest.fixture()
def source_doc_two_folders() -> Addict:
    return Addict({
        "first_folder": {
            "first_source": 75
        },
        "second_folder": {
            "second_source": 102,
        }
    })

@pytest.fixture()
def source_spec_two_folders() -> Addict:
    return Addict({
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
            "data_type": "folder",
            "sort_order": 0
        },
        "source_folder_2": {
            "name": "second_folder",
            "data_type": "folder",
            "sort_order": 1
        }
    })

@pytest.fixture()
def source_doc_nested() -> Addict:
    return Addict({
        "outer_s": {
            "first_source": 75,
            "inner_s": {
                "second_source": 102,
            }
        }
    })

@pytest.fixture()
def source_spec_nested() -> Addict:
    return Addict({
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
            "data_type": "folder",
            "sort_order": 0
        },
        "source_folder_2": {
            "name": "inner_s",
            "data_type": "folder",
            "parent": "source_folder_1",
            "sort_order": 1
        }
    })

@pytest.fixture()
def target_doc_flat() -> Addict:
    return Addict({
        "first_target": 75,
        "second_target": 102
    })

@pytest.fixture()
def target_spec_flat() -> Addict:
    return Addict({
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "sort_order": 1
        }
    })

@pytest.fixture()
def target_doc_one_folder() -> Addict:
    return Addict({
        "the_folder": {
            "first_target": 75,
            "second_target": 102
        }
    })

@pytest.fixture()
def target_spec_one_folder() -> Addict:
    return Addict({
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder",
            "sort_order": 1
        },
        "target_folder": {
            "name": "the_folder",
            "data_type": "folder",
            "sort_order": 0
        }
    })

@pytest.fixture()
def target_doc_two_folders() -> Addict:
    return Addict({
        "first_folder": {
            "first_target": 75
        },
        "second_folder": {
            "second_target": 102,
        }
    })

@pytest.fixture()
def target_spec_two_folders() -> Addict:
    return Addict({
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder_1",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder_2",
            "sort_order": 0
        },
        "target_folder_1": {
            "name": "first_folder",
            "data_type": "folder",
            "sort_order": 0
        },
        "target_folder_2": {
            "name": "second_folder",
            "data_type": "folder",
            "sort_order": 1
        }
    })

@pytest.fixture()
def target_doc_nested() -> Addict:
    return Addict({
        "outer_s": {
            "first_target": 75,
            "inner_s": {
                "second_target": 102,
            }
        }
    })

@pytest.fixture()
def target_spec_nested() -> Addict:
    return Addict({
        "target_var_1": {
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder_1",
            "sort_order": 0
        },
        "target_var_2": {
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder_2",
            "sort_order": 0
        },
        "target_folder_1": {
            "name": "outer_s",
            "data_type": "folder",
            "sort_order": 0
        },
        "target_folder_2": {
            "name": "inner_s",
            "data_type": "folder",
            "parent": "target_folder_1",
            "sort_order": 1
        }
    })

def do_translate(source_doc: Dict, source_specs: Dict, target_specs: Dict) -> Dict:
    source_track: Track = Track.build(source_specs)
    target_track: Track = Track.build(target_specs)
    translate: Translate = Translate(source_track, target_track)
    return translate(source_doc)

def test_flat_to_flat(source_doc_flat, source_spec_flat, target_doc_flat, target_spec_flat):
    target_spec_flat.target_var_1.sources = ["source_var_1"]
    target_spec_flat.target_var_2.sources = ["source_var_2"]
    actual: Dict = do_translate(source_doc_flat, source_spec_flat, target_spec_flat)
    assert actual == target_doc_flat

def test_flat_to_one_folder(source_doc_flat, source_spec_flat, target_doc_one_folder, target_spec_one_folder):
    target_spec_one_folder.target_var_1.sources = ["source_var_1"]
    target_spec_one_folder.target_var_2.sources = ["source_var_2"]
    actual: Dict = do_translate(source_doc_flat, source_spec_flat, target_spec_flat)
    assert actual == target_doc_flat

def test_flat_to_two_folders(source_doc_flat, source_spec_flat, target_doc_two_folders, target_spec_two_folders):
    target_spec_two_folders.target_var_1.sources = ["source_var_1"]
    target_spec_two_folders.target_var_2.sources = ["source_var_2"]
    actual: Dict = do_translate(source_doc_flat, source_spec_flat, target_spec_flat)
    assert actual == target_doc_flat
    pytest.fail()

def test_flat_to_nested(source_doc_flat, target_doc_nested):
    pytest.fail()

def test_one_folder_to_flat(source_doc_one_folder, target_doc_flat):
    pytest.fail()

def test_one_folder_to_one_folder(source_doc_one_folder, target_doc_one_folder):
    pytest.fail()

def test_one_folder_to_two_folder(source_doc_one_folder, target_doc_two_folders):
    pytest.fail()

def test_one_folder_to_nested(source_doc_one_folder, target_doc_nested):
    pytest.fail()

def test_two_folders_to_flat(source_doc_two_folders, target_doc_flat):
    pytest.fail()

def test_two_folders_to_one_folder(source_doc_two_folders, target_doc_one_folder):
    pytest.fail()

def test_two_folders_to_two_folder(source_doc_two_folders, target_doc_two_folders):
    pytest.fail()

def test_two_folders_to_nested(source_doc_two_folders, target_doc_nested):
    pytest.fail()

def test_nested_to_flat(source_doc_nested, target_doc_flat):
    pytest.fail()

def test_nested_to_one_folder(source_doc_nested, target_doc_one_folder):
    pytest.fail()

def test_nested_to_two_folder(source_doc_nested, target_doc_two_folders):
    pytest.fail()

def test_nested_to_nested(source_doc_nested, target_doc_nested):
    pytest.fail()
