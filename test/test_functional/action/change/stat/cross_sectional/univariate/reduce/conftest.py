from typing import Dict

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

@pytest.fixture()
def schema(spec_body) -> Schema:
    immutable: Track = Track.build(spec_body, None, "immutable")
    temporal: Track = Track.build({}, None, "temporal")
    schema: Schema = Schema(temporal, immutable)
    return schema

@pytest.fixture()
def i_composite(schema, content_body) -> Composite:
    content: Dict = {
        "immutable": content_body
    }
    return Composite(schema, content)
