import pytest
from typing import Dict, Iterable

@pytest.fixture()
def source_doc_flat() -> Dict:
    return {
        "first_source": 75,
        "second_source": 102
    }

@pytest.fixture()
def source_spec_flat() -> Iterable[Dict]:
    return [
        {
            "_id": "source_var_1",
            "name": "first_source",
            "data_type": "Integer"
        },
        {
            "_id": "source_var_2",
            "name": "second_source",
            "data_type": "Integer"
        }
    ]

@pytest.fixture()
def source_doc_one_folder() -> Dict:
    return {
        "the_folder": {
            "first_source": 75,
            "second_source": 102
        }
    }

@pytest.fixture()
def source_spec_one_folder() -> Iterable[Dict]:
    return [
        {
            "_id": "source_var_1",
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder"
        },
        {
            "_id": "source_var_2",
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder"
        },
        {
            "_id": "source_folder",
            "name": "the_folder",
            "data_type": "folder"
        }
    ]

@pytest.fixture()
def source_doc_two_folders() -> Dict:
    return {
        "first_folder": {
            "first_source": 75
        },
        "second_folder": {
            "second_source": 102,
        }
    }

@pytest.fixture()
def source_spec_two_folders() -> Iterable[Dict]:
    return [
        {
            "_id": "source_var_1",
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder_1"
        },
        {
            "_id": "source_var_2",
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder_2"
        },
        {
            "_id": "source_folder_1",
            "name": "first_folder",
            "data_type": "folder"
        },
        {
            "_id": "source_folder_2",
            "name": "second_folder",
            "data_type": "folder"
        }
    ]

@pytest.fixture()
def source_doc_nested() -> Dict:
    return {
        "outer_s": {
            "first_source": 75,
            "inner_s": {
                "second_source": 102,
            }
        }
    }

@pytest.fixture()
def source_spec_nested() -> Iterable[Dict]:
    return [
        {
            "_id": "source_var_1",
            "name": "first_source",
            "data_type": "Integer",
            "parent": "source_folder_1"
        },
        {
            "_id": "source_var_2",
            "name": "second_source",
            "data_type": "Integer",
            "parent": "source_folder_2"
        },
        {
            "_id": "source_folder_1",
            "name": "outer_s",
            "data_type": "folder"
        },
        {
            "_id": "source_folder_2",
            "name": "inner_s",
            "data_type": "folder",
            "parent": "source_folder_1"
        }
    ]

@pytest.fixture()
def target_doc_flat() -> Dict:
    return {
        "first_target": 75,
        "second_target": 102
    }

@pytest.fixture()
def target_spec_flat() -> Iterable[Dict]:
    return [
        {
            "_id": "target_var_1",
            "name": "first_target",
            "data_type": "Integer"
        },
        {
            "_id": "target_var_2",
            "name": "second_target",
            "data_type": "Integer"
        }
    ]

@pytest.fixture()
def target_doc_one_folder() -> Dict:
    return {
        "target_folder": {
            "first_target": 75,
            "second_target": 102
        }
    }

@pytest.fixture()
def target_spec_one_folder() -> Iterable[Dict]:
    return [
        {
            "_id": "target_var_1",
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder"
        },
        {
            "_id": "target_var_2",
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder"
        },
        {
            "_id": "target_folder",
            "name": "the_folder",
            "data_type": "folder"
        }
    ]

@pytest.fixture()
def target_doc_two_folder() -> Dict:
    return {
        "first_target_folder": {
            "first_target": 75
        },
        "second_target_folder": {
            "second_target": 102
        }
    }

@pytest.fixture()
def target_spec_two_folders() -> Iterable[Dict]:
    return [
        {
            "_id": "target_var_1",
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder_1"
        },
        {
            "_id": "target_var_2",
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder_2"
        },
        {
            "_id": "target_folder_1",
            "name": "first_folder",
            "data_type": "folder"
        },
        {
            "_id": "target_folder_2",
            "name": "second_folder",
            "data_type": "folder"
        }
    ]

@pytest.fixture()
def target_doc_nested() -> Dict:
    return {
        "outer_t": {
            "first_target": 75,
            "inner_t": {
                "second_target": 102
            }
        }
    }

@pytest.fixture()
def target_spec_nested() -> Iterable[Dict]:
    return [
        {
            "_id": "target_var_1",
            "name": "first_target",
            "data_type": "Integer",
            "parent": "target_folder_1"
        },
        {
            "_id": "target_var_2",
            "name": "second_target",
            "data_type": "Integer",
            "parent": "target_folder_2"
        },
        {
            "_id": "target_folder_1",
            "name": "outer_s",
            "data_type": "folder"
        },
        {
            "_id": "target_folder_2",
            "name": "inner_s",
            "data_type": "folder",
            "parent": "target_folder_1"
        }
    ]

def test_flat_to_flat(source_doc_flat, source_spec_flat, target_doc_flat, target_spec_flat):
    pytest.fail()

def test_flat_to_one_folder(source_doc_flat, target_doc_one_folder):
    pytest.fail()

def test_flat_to_two_folders(source_doc_flat, target_doc_two_folder):
    pytest.fail()

def test_flat_to_nested(source_doc_flat, target_doc_nested):
    pytest.fail()

def test_one_folder_to_flat(source_doc_one_folder, target_doc_flat):
    pytest.fail()

def test_one_folder_to_one_folder(source_doc_one_folder, target_doc_one_folder):
    pytest.fail()

def test_one_folder_to_two_folder(source_doc_one_folder, target_doc_two_folder):
    pytest.fail()

def test_one_folder_to_nested(source_doc_one_folder, target_doc_nested):
    pytest.fail()

def test_two_folders_to_flat(source_doc_two_folders, target_doc_flat):
    pytest.fail()

def test_two_folders_to_one_folder(source_doc_two_folders, target_doc_one_folder):
    pytest.fail()

def test_two_folders_to_two_folder(source_doc_two_folders, target_doc_two_folder):
    pytest.fail()

def test_two_folders_to_nested(source_doc_two_folders, target_doc_nested):
    pytest.fail()

def test_nested_to_flat(source_doc_nested, target_doc_flat):
    pytest.fail()

def test_nested_to_one_folder(source_doc_nested, target_doc_one_folder):
    pytest.fail()

def test_nested_to_two_folder(source_doc_nested, target_doc_two_folder):
    pytest.fail()

def test_nested_to_nested(source_doc_nested, target_doc_nested):
    pytest.fail()
