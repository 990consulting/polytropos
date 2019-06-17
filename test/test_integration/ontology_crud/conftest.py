from typing import Dict

import pytest

from polytropos.ontology.track import Track

@pytest.fixture()
def simple_spec() -> Dict:
    return {
        "target_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_var_id": {
            "name": "the_target",
            "data_type": "Integer",
            "sort_order": 0,
            "parent": "target_folder"
        }
    }

@pytest.fixture()
def simple_flat_spec() -> Dict:
    return {
        "target_folder": {
            "name": "the_folder",
            "data_type": "Folder",
            "sort_order": 1
        },
        "target_var_id": {
            "name": "the_target",
            "data_type": "Integer",
            "sort_order": 0
        }
    }

@pytest.fixture()
def simple_track(simple_spec) -> Track:
    return Track.build(simple_spec, None, "Sample")

@pytest.fixture()
def simple_flat_track(simple_flat_spec) -> Track:
    return Track.build(simple_flat_spec, None, "Sample")

@pytest.fixture()
def source_nested_dict_track() -> Track:
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
        },
        "source_var_3": {
            "name": "third_source",
            "data_type": "Integer",
            "parent": "source_folder_2",
            "sort_order": 1
        },
        "source_folder_3": {
            "name": "initially_empty_folder",
            "data_type": "Folder",
            "sort_order": 1
        }
    }
    return Track.build(spec, None, "Source")

@pytest.fixture()
def target_nested_dict_track(source_nested_dict_track) -> Track:
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
    return Track.build(spec, source_nested_dict_track, "Target")

@pytest.fixture()
def source_list_track() -> Track:
    spec: Dict = {
        "source_folder": {
            "name": "source_outer_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_list": {
            "name": "source_inner_list",
            "data_type": "List",
            "parent": "source_folder",
            "sort_order": 0,
        },
        "source_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 0
        },
        "source_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_list",
            "sort_order": 1
        },
        "source_named_list": {
            "name": "source_inner_named_list",
            "data_type": "NamedList",
            "parent": "source_folder",
            "sort_order": 1
        },
        "source_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "source_named_list",
            "sort_order": 0
        },
        "random_text_field": {
            "name": "I'm not part of the list",
            "data_type": "Text",
            "sort_order": 1
        }
    }
    return Track.build(spec, None, "Source")

@pytest.fixture()
def target_list_track(source_list_track) -> Track:
    spec: Dict = {
        "target_folder_outer": {
            "name": "outer",
            "data_type": "Folder",
            "sort_order": 0
        },
        "target_folder_inner": {
            "name": "inner",
            "data_type": "Folder",
            "parent": "target_folder_outer",
            "sort_order": 0
        },
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "parent": "target_folder_outer",
            "sort_order": 1,
            "sources": ["source_list"]
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0,
            "sources": ["source_list_name"]
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 1,
            "sources": ["source_list_color"]
        },
        "target_named_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "parent": "target_folder_inner",
            "sort_order": 0,
            "sources": ["source_named_list"]
        },
        "target_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_named_list",
            "sort_order": 0,
            "sources": ["source_named_list_color"]
        }
    }
    return Track.build(spec, source_list_track, "Target")

@pytest.fixture()
def source_named_list_track() -> Track:
    spec: Dict = {
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
        },
        "random_text_field": {
            "name": "I'm not part of the list",
            "data_type": "Text",
            "sort_order": 2
        }
    }
    return Track.build(spec, None, "Source")

@pytest.fixture()
def target_named_list_track(source_named_list_track) -> Track:
    spec: Dict = {
        "target_root": {
            "name": "People",
            "data_type": "NamedList",
            "sources": ["source_root_1", "source_root_2"],
            "sort_order": 0
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
    return Track.build(spec, source_named_list_track, "Target")

@pytest.fixture
def source_nested_list_track():
    source_spec: Dict = {
        "outer_list_1_id": {
            "name": "outer_list_1",
            "data_type": "List",
            "sort_order": 0
        },
        "descended_from_outer_list": {
            "name": "I am descended from the outer list",
            "data_type": "Text",
            "sort_order": 1
        },
        "inner_list_1_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_1_id",
            "sort_order": 0
        },
        "name_1_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_1_id",
            "sort_order": 0
        },
        "outer_list_2_id": {
            "name": "outer_list_2",
            "data_type": "List",
            "sort_order": 0
        },
        "inner_list_2_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_2_id",
            "sort_order": 0
        },
        "name_2_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_2_id",
            "sort_order": 0
        }
    }
    return Track.build(source_spec, None, "Source")

@pytest.fixture
def target_nested_list_track(source_nested_list_track):
    target_spec: Dict = {
        "outer_list_id": {
            "name": "outer_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["outer_list_1_id", "outer_list_2_id"]
        },
        "inner_list_id": {
            "name": "inner_list",
            "data_type": "List",
            "parent": "outer_list_id",
            "sort_order": 0,
            "sources": ["inner_list_1_id", "inner_list_2_id"]
        },
        "name_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_list_id",
            "sort_order": 0,
            "sources": ["name_1_id", "name_2_id"]
        }
    }
    return Track.build(target_spec, source_nested_list_track, "Target")

@pytest.fixture
def source_nested_named_list_track():
    source_spec: Dict = {
        "outer_list_1_id": {
            "name": "outer_list_1",
            "data_type": "List",
            "sort_order": 0
        },
        "inner_named_list_1_id": {
            "name": "inner_named_list",
            "data_type": "NamedList",
            "parent": "outer_list_1_id",
            "sort_order": 0
        },
        "descended_from_outer_list": {
            "name": "I am descended from the outer list",
            "data_type": "Text",
            "sort_order": 1
        },
        "name_1_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_named_list_1_id",
            "sort_order": 0
        },
        "outer_list_2_id": {
            "name": "outer_list_2",
            "data_type": "List",
            "sort_order": 0
        },
        "inner_named_list_2_id": {
            "name": "inner_named_list",
            "data_type": "NamedList",
            "parent": "outer_list_2_id",
            "sort_order": 0
        },
        "name_2_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_named_list_2_id",
            "sort_order": 0
        }
    }
    return Track.build(source_spec, None, "Source")

def target_nested_named_list_track(source_nested_named_list_track):
    target_spec: Dict = {
        "outer_list_id": {
            "name": "outer_list",
            "data_type": "List",
            "sort_order": 0,
            "sources": ["outer_list_1_id", "outer_list_2_id"]
        },
        "inner_named_list_id": {
            "name": "inner_named_list",
            "data_type": "NamedList",
            "parent": "outer_list_id",
            "sort_order": 0,
            "sources": ["inner_named_list_1_id", "inner_named_list_2_id"]
        },
        "name_id": {
            "name": "name",
            "data_type": "Text",
            "parent": "inner_named_list_id",
            "sort_order": 0,
            "sources": ["name_1_id", "name_2_id"]
        }
    }
    return Track.build(target_spec, source_nested_named_list_track, "Target")
