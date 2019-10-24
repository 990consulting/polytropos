import json
import os
from typing import Dict, Callable
from unittest.mock import MagicMock
import shutil

import pytest

from polytropos.ontology.schema import Schema
from polytropos.ontology.context import Context
from polytropos.actions.translate import Translate, Translator
from polytropos.ontology.track import Track

basepath: str = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture()
def source_schema() -> Schema:
    spec_path: str = os.path.join(basepath, "source_spec.json")
    with open(spec_path) as fh:
        spec: Dict = json.load(fh)
    temporal: Track = Track.build(spec, None, "temporal")
    immutable: Track = Track.build({}, None, "immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def target_schema(source_schema) -> Schema:
    spec_path: str = os.path.join(basepath, "target_spec.json")
    with open(spec_path) as fh:
        spec: Dict = json.load(fh)
    temporal: Track = Track.build(spec, source_schema.temporal, "temporal")
    immutable: Track = Track.build({}, source_schema.immutable, "immutable")
    return Schema(temporal, immutable)

@pytest.fixture()
def translate(source_schema, target_schema) -> Translate:
    context: Context = Context("", "", "", "", "", "", "", False, 1, False, True)
    translate_immutable: Translator = Translator(target_schema.immutable, Translate.create_document_value_provider)
    translate_temporal: Translator = Translator(target_schema.temporal, Translate.create_document_value_provider)
    return Translate(context, target_schema, translate_immutable, translate_temporal)

def test_regression_20191024(translate):
    input_path: str = os.path.join(basepath, "input.json")
    with open(input_path) as fh:
        content: Dict = json.load(fh)
    expected_path: str = os.path.join(basepath, "expected.json")
    with open(expected_path) as fh:
        expected: Dict = json.load(fh)
    actual: Dict = translate.do_translate(content, "the_composite")
    assert actual == expected
