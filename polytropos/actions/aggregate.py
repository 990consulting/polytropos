import os
import json
from dataclasses import dataclass
from abc import abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator

from polytropos.actions.step import Step
from polytropos.util.loader import load
from polytropos.ontology.schema import Schema


@dataclass
class Aggregate(Step):
    """Iterates over all composites following one schema, and produces a new set of composites, representing a different
    kind of entity, and following a different schema."""
    target_schema: Schema

    @classmethod
    def build(
            cls, path_locator, schema, name, target_schema, id_var,
            input_schema_vars, output_schema_vars
    ): 
        target_schema = Schema.load(path_locator, target_schema)
        aggregations = load(path_locator.aggregations_dir, cls)
        input_variables = {
            var_name: schema.get(var_id)
            for var_name, var_id in input_schema_vars.items()
        }
        output_variables = {
            var_name: target_schema.get(var_id)
            for var_name, var_id in output_schema_vars.items()
        }
        return aggregations[name](target_schema=target_schema, **input_variables, **output_variables)

    @abstractmethod
    def extract(self, composite: Dict) -> Optional[Any]:
        """Gather the information to be used in the analysis."""
        pass

    @abstractmethod
    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        """Collect, process, and store the global information provided from each composite during the scan() step.
        :param extracts: Tuple of (composite id, whatever is returned by extract)"""
        pass

    @abstractmethod
    def emit(self) -> Iterator[Tuple[str, Dict]]:
        """Lazily produce instances of the target entity. Yields tuples of (new entity ID, new entity content)."""
        pass

    def __call__(self, origin, target):
        extracts = []
        for filename in os.listdir(origin):
            with open(os.path.join(origin, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                extracts.append((filename, self.extract(composite)))
        self.analyze(extracts)
        for filename, composite in self.emit():
            with open(os.path.join(target, filename + '.json'), 'w') as target_file:
                json.dump(composite, target_file)