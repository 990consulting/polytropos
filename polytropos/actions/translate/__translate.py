from dataclasses import dataclass
import os
import json
from typing import Any

from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.actions.translate import Translator


@dataclass
class Translate(Step):
    target_schema: Schema
    # TODO: Better typing, Callable??
    translate_immutable: Any
    translate_temporal: Any

    """Wrapper around the tranlation functions to be used in the tasks"""
    @classmethod
    def build(cls, path_locator, schema, target_schema):
        target_schema = Schema.load(path_locator, target_schema, schema)
        translate_immutable = Translator(target_schema.immutable)
        translate_temporal = Translator(target_schema.temporal)
        return cls(target_schema, translate_immutable, translate_temporal)

    def __call__(self, origin, target):
        for filename in os.listdir(origin):
            translated = {}
            with open(os.path.join(origin, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                for key, value in composite.items():
                    if key.isdigit():
                        translated[key] = self.translate_temporal(value)
                    elif key == 'immutable':
                        translated[key] = self.translate_immutable(value)
                    else:
                        pass
            with open(os.path.join(target, filename), 'w') as target_file:
                json.dump(translated, target_file)

