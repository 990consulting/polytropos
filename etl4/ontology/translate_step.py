from dataclasses import dataclass
import os
import json
from abc import abstractmethod
from collections.abc import Callable
from typing import Dict, Optional, Any, Iterable, Tuple

from etl4.ontology.step import Step
from etl4.ontology.schema import Schema
from etl4.transform.translate import Translate


@dataclass
class TranslateStep(Step):
    # TODO: Better typing, Callable??
    translate_invariant: Any
    translate_temporal: Any
    """Wrapper around the tranlation functions to be used in the tasks"""
    @classmethod
    def build(cls, path_locator, schema, target_schema):
        target_schema = Schema.load(path_locator, target_schema, schema)
        translate_invariant = Translate(
            schema.invariant, target_schema.invariant
        )
        translate_temporal = Translate(
            schema.temporal, target_schema.temporal
        )
        return cls(translate_invariant, translate_temporal)

    def __call__(self, origin, target):
        for filename in os.listdir(origin):
            with open(os.path.join(origin, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                invariant = self.translate_invariant(composite)
                temporal = self.translate_temporal(composite)
            with open(os.path.join(target, filename), 'w') as target_file:
                json.dump(invariant, target_file)

