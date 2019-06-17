from dataclasses import dataclass
import os
import json
from typing import Any, TYPE_CHECKING

from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.actions.translate import Translator

if TYPE_CHECKING:
    from polytropos.ontology.paths import PathLocator

@dataclass
class Translate(Step):
    target_schema: Schema
    translate_immutable: Translator
    translate_temporal: Translator

    """Wrapper around the tranlation functions to be used in the tasks"""
    @classmethod
    def build(cls, path_locator: "PathLocator", source_schema: Schema, target_schema_path: str):
        target_schema: Schema = Schema.load(path_locator, target_schema_path, source_schema=source_schema)
        translate_immutable: Translator = Translator(target_schema.immutable)
        translate_temporal: Translator = Translator(target_schema.temporal)
        return cls(target_schema, translate_immutable, translate_temporal)

    def __call__(self, origin_dir: str, target_dir: str):
        for filename in os.listdir(origin_dir):
            translated = {}
            with open(os.path.join(origin_dir, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                for key, value in composite.items():
                    if key.isdigit():
                        translated[key] = self.translate_temporal(value)
                    elif key == 'immutable':
                        translated[key] = self.translate_immutable(value)
                    else:
                        pass
            with open(os.path.join(target_dir, filename), 'w') as target_file:
                json.dump(translated, target_file)

