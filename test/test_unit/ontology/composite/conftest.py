from typing import Dict

import pytest

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture
def trivial_schema() -> Schema:
    t = Track.build({}, None, "")
    i = Track.build({}, None, "")
    schema = Schema(t, i)
    return schema

@pytest.fixture
def immutable_list_schema() -> Schema:
    temporal_track: Track = Track.build({}, None, "")

    immutable_spec: Dict = {
        "source_root_2": {
            "name": "list_source_2",
            "data_type": "List",
            "sort_order": 0,
        },
        "the_folder": {
            "name": "inner_folder",
            "data_type": "Folder",
            "sort_order": 0
        },
        "source_root_2_nombre": {
            "name": "nombre",
            "data_type": "Text",
            "parent": "the_folder",
            "sort_order": 0
        },
        "source_root_2_edad": {
            "name": "edad",
            "data_type": "Integer",
            "parent": "the_folder",
            "sort_order": 1
        },
        "source_root_2_helado": {
            "name": "helado",
            "data_type": "Text",
            "parent": "source_root_2",
            "sort_order": 1
        }
    }

    immutable_track: Track = Track.build(immutable_spec, None, "")
    return Schema(temporal_track, immutable_track)
