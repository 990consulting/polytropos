"""Bug discovered 2020-08-26: an empty folder inside an empty list inside an empty folder was not pruned. This test
represents a near-exact duplication of the relevant content and verifies that it does now get pruned."""
from typing import Dict

from polytropos.actions.changes.prune import Prune
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

def test_regression_20200826():
    temporal_spec: Dict = {
        "tax_return_sources": {
            "name": "Tax return",
            "data_type": "Folder",
            "sort_order": 0
        },
        "logical_temporal_001543": {
            "name": "Schedule B",
            "data_type": "Folder",
            "parent": "tax_return_sources",
            "sort_order": 0
        },
        "logical_temporal_001544": {
            "name": "Part I",
            "data_type": "List",
            "parent": "logical_temporal_001543",
            "sort_order": 0
        },
        "logical_temporal_001545": {
            "name": "Column A",
            "data_type": "Integer",
            "parent": "logical_temporal_001544",
            "sort_order": 0
        },
        "something_else": {
            "name": "Something else",
            "data_type": "Text",
            "sort_order": 1
        }
    }
    temporal_track: Track = Track.build(temporal_spec, None, "temporal")
    immutable_track: Track = Track.build({}, None, "immutable")
    schema: Schema = Schema(temporal_track, immutable_track)
    content: Dict = {
        "201012": {
            "Tax return": {
                "Schedule B": {
                    "Part I": [
                        {}
                    ]
                }
            },
            "Something else": "should not get pruned"
        }
    }
    composite: Composite = Composite(schema, content)
    prune: Prune = Prune(schema, {})

    expected: Dict = {
        "201012": {
            "Something else": "should not get pruned"
        }
    }
    prune(composite)
    assert composite.content == expected