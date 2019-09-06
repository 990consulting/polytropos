from typing import Dict

import pytest
from polytropos.ontology.composite import Composite

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
            "parent": "source_root_2",
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

@pytest.fixture
def immutable_keyed_list_schema() -> Schema:
    temporal_track: Track = Track.build({}, None, "")

    immutable_spec: Dict = {
        "source_root_2": {
            "name": "keyed_list_source_2",
            "data_type": "KeyedList",
            "sort_order": 0,
        },
        "the_folder": {
            "name": "inner_folder",
            "data_type": "Folder",
            "parent": "source_root_2",
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

@pytest.fixture
def simple_schema() -> Schema:
    temporal_spec: Dict = {
        "the_weight_var": {
            "name": "weight_in_pounds",
            "data_type": "Decimal",
            "sort_order": 0
        }
    }
    temporal_track: Track = Track.build(temporal_spec, None, "temporal")

    immutable_spec: Dict = {
        "the_person_name_var": {
            "name": "first_name",
            "data_type": "Text",
            "sort_order": 0
        },
        "the_gender_var": {
            "name": "gender",
            "data_type": "Text",
            "sort_order": 1
        },
        "the_weight_gain_var": {
            "name": "total_weight_gain",
            "data_type": "Decimal",
            "sort_order": 2
        },
        "the_sentence_var": {
            "name": "personal_summary",
            "data_type": "Text",
            "sort_order": 3
        },
        "color_folder": {
            "name": "color_info",
            "data_type": "Folder",
            "sort_order": 4
        },
        "the_color_var": {
            "name": "favorite_color",
            "data_type": "Text",
            "parent": "color_folder",
            "sort_order": 0
        },
        "the_rgb_var": {
            "name": "rgb_value",
            "data_type": "Text",
            "parent": "color_folder",
            "sort_order": 1
        }
    }

    immutable_track: Track = Track.build(immutable_spec, None, "immutable")
    return Schema(temporal_track, immutable_track)

@pytest.fixture
def simple_doc() -> Dict:
    return {
        "immutable": {
            "first_name": "Steve",
            "gender": "male",
            "total_weight_gain": 3.9,
            "personal_summary": "Steve's favorite color is orange (FFA000). Over the observation period, he gained"
                                " 3.9 lbs.",
            "color_info": {
                "favorite_color": "orange",
                "rgb_value": "FFA000"
            }
        },
        "2013": {
            "weight_in_pounds": 172.3
        },
        "2010": {
            "weight_in_pounds": 168.4
        },
        "2011": {
            "weight_in_pounds": 170.1
        },
        "2012": {
            "weight_in_pounds": 174.2
        }
    }

@pytest.fixture
def simple_composite(simple_schema, simple_doc) -> Composite:
    return Composite(simple_schema, simple_doc)
