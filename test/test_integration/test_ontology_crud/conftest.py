from typing import Dict

import pytest

from etl4.ontology.track import Track
from etl4.ontology.variable import Variable

@pytest.fixture()
def simple_spec() -> Dict:
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
    return Track(simple_spec, None, "Sample")

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
        }
    }
    return Track(spec, None, "Source")

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
            "sources": ["source_list"],
            "source_child_mappings": {
                "source_list": {
                    "target_list_name": ["source_list_name"],
                    "target_list_color": ["source_list_color"]
                }
            }
        },
        "target_list_name": {
            "name": "name",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 0
        },
        "target_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_list",
            "sort_order": 1
        },
        "target_named_list": {
            "name": "the_named_list",
            "data_type": "NamedList",
            "parent": "target_folder_inner",
            "sort_order": 0,
            "sources": ["source_named_list"],
            "source_child_mappings": {
                "source_named_list": {
                    "target_named_list_color": ["source_named_list_color"]
                }
            }
        },
        "target_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_named_list",
            "sort_order": 0
        }
    }
    return Track(spec, source_list_track, "Target")

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
    }
    return Track.build(spec, source_named_list_track, "Target")
