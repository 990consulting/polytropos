import pytest
from typing import Dict

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "source_outer_folder": {
            "source_inner_list": [
                {
                    "name": "Steve",
                    "color": "red"
                },
                {
                    "name": "Samantha",
                    "color": "blue"
                }
            ],
            "source_inner_named_list": {
                "Anne": {
                    "color": "orange"
                },
                "Janet": {
                    "color": "green"
                }
            }
        }
    }

@pytest.fixture()
def source_spec() -> Dict:
    return {
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

@pytest.fixture()
def target_flattened_doc() -> Dict:
   return {
       "the_list": [
           {
               "name": "Steve",
               "color": "red"
           },
           {
               "name": "Samantha",
               "color": "blue"
           }
       ],
       "the_named_list": {
           "anne": {
               "color": "orange"
           },
           "janet": {
               "color": "green"
           }
       }
   }

@pytest.fixture()
def target_flattened_spec() -> Dict:
    return {
        "target_list": {
            "name": "the_list",
            "data_type": "List",
            "sort_order": 0,
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
            "sort_order": 1,
            "sources": ["source_named_list"],
            "source_child_mappings": {
                "target_named_list_color": ["source_named_list_color"]
            }
        },
        "target_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_named_list",
            "sort_order": 0
        }
    }

@pytest.fixture()
def target_nested_doc() -> Dict:
    return {
        "outer": {
            "inner": {
                "the_named_list": {
                    "anne": {
                        "color": "orange"
                    },
                    "janet": {
                        "color": "green"
                    }
                }
            },
            "the_list": [
                {
                    "name": "Steve",
                    "color": "red"
                },
                {
                    "name": "Samantha",
                    "color": "blue"
                }
            ]
        }
    }

@pytest.fixture()
def target_nested_spec() -> Dict:
    return {
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
                "target_named_list_color": ["source_named_list_color"]
            }
        },
        "target_named_list_color": {
            "name": "color",
            "data_type": "Text",
            "parent": "target_named_list",
            "sort_order": 0
        }
    }

