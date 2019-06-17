import os
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from polytropos.util.loader import load
from polytropos.actions.step import Step
from polytropos.util.config import MAX_WORKERS


@dataclass
class Filter(Step):
    """Iterates over each composite, removing some of them if they do not meet some criterion."""

    @classmethod
    def build(cls, path_locator, schema, name, subjects):
        filters = load(cls)
        variables = {
            var_name: schema.get(var_id)
            for var_name, var_id in subjects.items()
        }
        return filters[name](**variables)

    @abstractmethod
    def passes(self, composite: Dict) -> bool:
        pass

    def process_composite(self, origin, target, filename):
        with open(os.path.join(origin, filename), 'r') as origin_file:
            composite = json.load(origin_file)
            if self.passes(composite):
                with open(os.path.join(target, filename), 'w') as target_file:
                    json.dump(composite, target_file)

    def __call__(self, origin, target):
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(
                partial(self.process_composite, origin, target),
                os.listdir(origin)
            )
