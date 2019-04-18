import pytest
from typing import Dict, Iterable

@pytest.fixture()
def source_doc() -> Dict:
    return {
        "list_source_1": [
            {
                "name": "Steve",
                "nom": "Etienne",  # There are two sources for name in list_source_1; sources are checked in order.
                "age": 32,
                "ice cream": "strawberry",
                "sport": "tennis"
            },
            {
                "nom": "Hannah",
                "ice cream": "rocky road",
            }
        ],
        "list_source_2": [
            {
                "nombre": "Stacy",
                "edad": 26,
                "helado": "chocolate"
            }
        ]
    }

@pytest.fixture()
def target_doc() -> Dict:
    return {
        "People": [
            {
                "Name": "Steve",
                "Age": 32,
                "Ice cream": "strawberry",
                "Sport": "tennis"
            },
            {
                "Name": "Hannah",
                "Age": None,
                "Ice cream": "rocky road",
                "Sport": None
            },
            {
                "Name": "Stacy",
                "Age": 26,
                "Ice cream": "chocolate",
                "Sport": None
            }
        ]
    }

@pytest.fixture()
def source_spec() -> Iterable[Dict]:
    return [
        {
            "_id": "source_root_1",
            "name": "list_source_1",
            "data_type": "ListContainer",
            "local": True,
            "temporal": False
        },
        {
            "_id": "source_root_1_name",
            "name": "name",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "source_root_1"
        },
        {
            "_id": "source_root_1_nom",
            "name": "nom",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "source_root_1"
        },
        {
            "_id": "source_root_1_age",
            "name": "age",
            "data_type": "Integer",
            "local": True,
            "temporal": False,
            "parent": "source_root_1"
        },
        {
            "_id": "source_root_1_ice_cream",
            "name": "ice cream",
            "data_type": "text",
            "local": True,
            "temporal": False,
            "parent": "source_root_1"
        },
        {
            "_id": "source_root_1_sport",
            "name": "sport",
            "data_type": "text",
            "local": True,
            "temporal": False,
            "parent": "source_root_1"
        },
        {
            "_id": "source_root_2",
            "name": "list_source_2",
            "data_type": "ListContainer",
            "local": True,
            "temporal": False
        },
        {
            "_id": "source_root_2_nombre",
            "name": "nombre",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "source_root_2"
        },
        {
            "_id": "source_root_2_edad",
            "name": "edad",
            "data_type": "Integer",
            "local": True,
            "temporal": False,
            "parent": "source_root_2"
        },
        {
            "_id": "source_root_2_helado",
            "name": "helado",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "source_root_2"
        }
    ]

@pytest.fixture()
def target_spec() -> Iterable[Dict]:
    return [
        {
            "_id": "target_root",
            "name": "People",
            "data_type": "ListContainer",
            "local": True,
            "temporal": False,
            "sources": ["source_root_1", "source_root_2"],
            "source_child_mappings": {
                "source_root_1": {
                    "target_root_name": ["source_root_1_name", "source_root_1_nom"],
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
        {
            "_id": "target_root_name",
            "name": "Name",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "target_root"
        },
        {
            "_id": "target_root_age",
            "name": "Age",
            "data_type": "Integer",
            "local": True,
            "temporal": False,
            "parent": "target_root"
        },
        {
            "_id": "target_root_ice_cream",
            "name": "Ice cream",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "target_root"
        },
        {
            "_id": "target_root_sport",
            "name": "Sport",
            "data_type": "Text",
            "local": True,
            "temporal": False,
            "parent": "target_root"
        }
    ]
