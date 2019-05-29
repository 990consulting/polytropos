from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Dict

from etl4.ontology.task.__loader import load
from etl4.ontology.step import Step


@dataclass
class Filter(Step):
    """Iterates over each composite, removing some of them if they do not meet some criterion."""

    @classmethod
    def build(cls, path_locator, schema, name, subjects):
        filters = load(path_locator.filters_dir, path_locator.filters_import, cls)
        variables = {
            var_name: schema.get(var_id)
            for var_name, var_id in subjects.items()
        }
        return filters[name](**variables)

    @abstractmethod
    def passes(self, composite: Dict) -> bool:
        pass

    def __call__(self, data):
        pass
