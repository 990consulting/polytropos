import json
import os

from typing import Dict, Callable

import pytest
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

@pytest.fixture()
def schema(basepath) -> Schema:
    path: str = os.path.join(basepath, "..", "examples", "s_7_csv", "conf", "schemas")
    return Schema.load("composite", base_path=path)

@pytest.fixture()
def read_composite(schema, basepath) -> Callable:
    def _read_composite(composite_number: int) -> Composite:
        filename: str = "composite_%i.json" % composite_number
        filepath: str = os.path.join(basepath, "..", "examples", "s_7_csv", "data", "entities", "com", "pos", "ite",
                                     filename)
        with open(filepath) as fh:
            content: Dict = json.load(fh)
        return Composite(schema, content, composite_id=filename[:-5])
    return _read_composite
