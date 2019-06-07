from dataclasses import dataclass
import os
import json
from abc import abstractmethod
from collections.abc import Callable
from typing import Dict, Optional, Any, Iterable, Tuple

from polytropos.ontology.step import Step
from polytropos.ontology.schema import Schema
from polytropos.transform.translate import Translate


@dataclass
class TranslateStep(Step):
    target_schema: Schema
    # TODO: Better typing, Callable??
    translate_invariant: Any
    translate_temporal: Any
    """Wrapper around the tranlation functions to be used in the tasks"""
    @classmethod
    def build(cls, path_locator, schema, target_schema):
        target_schema = Schema.load(path_locator, target_schema, schema)
        translate_invariant = Translate(target_schema.invariant)
        translate_temporal = Translate(target_schema.temporal)
        return cls(target_schema, translate_invariant, translate_temporal)

    def __call__(self, origin, target):
        for filename in os.listdir(origin):
            translated = {}
            with open(os.path.join(origin, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                for key, value in composite.items():
                    if key.isdigit():
                        translated[key] = self.translate_temporal(value)
                    elif key == 'invariant':
                        translated[key] = self.translate_invariant(value)
                    else:
                        pass
            with open(os.path.join(target, filename), 'w') as target_file:
                json.dump(translated, target_file)

