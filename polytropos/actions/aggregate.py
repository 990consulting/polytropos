import os
import json
from dataclasses import dataclass
from abc import abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator, Type
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from polytropos.ontology.composite import Composite

from polytropos.actions.step import Step
from polytropos.ontology.paths import PathLocator
from polytropos.ontology.variable import Variable
from polytropos.util.loader import load
from polytropos.ontology.schema import Schema
from polytropos.util.config import MAX_WORKERS


@dataclass
class Aggregate(Step):
    """Iterates over all composites following one schema, and produces a new set of composites, representing a different
    kind of entity, and following a different schema."""
    origin_schema: Schema
    target_schema: Schema
    id_var: str

    # noinspection PyMethodOverriding
    @classmethod
    def build(
            cls, path_locator: PathLocator, schema: Schema, name: str, target_schema: str, id_var: str,
            input_mappings: Dict, output_mappings: Dict
    ): 
        target_schema_instance: Schema = Schema.load(target_schema, path_locator=path_locator)
        aggregations: Dict[str, Type] = load(cls)
        return aggregations[name](origin_schema=schema, target_schema=target_schema_instance, id_var=id_var,
                                  **input_mappings, **output_mappings)

    @abstractmethod
    def extract(self, composite: Composite) -> Optional[Any]:
        """Gather the information to be used in the analysis."""
        pass

    @abstractmethod
    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        """Collect, process, and store the global information provided from each composite during the scan() step.
        :param extracts: Tuple of (composite id, whatever is returned by extract)"""
        pass

    @abstractmethod
    def emit(self) -> Iterator[Tuple[str, Composite]]:
        """Lazily produce instances of the target entity. Yields tuples of (new entity ID, new entity composite)."""
        pass

    def process_composite(self, origin_dir: str, filename: str):
        with open(os.path.join(origin_dir, filename), 'r') as origin_file:
            content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.origin_schema, content)
            return filename, self.extract(composite)

    def write_composite(self, target_dir: str, emission: Composite):
        filename, composite = emission
        with open(os.path.join(target_dir, filename + '.json'), 'w') as target_file:
            json.dump(composite.content, target_file, indent=2)

    def __call__(self, origin_dir: str, target_dir: str):
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            self.analyze(
                executor.map(
                    partial(self.process_composite, origin_dir),
                    os.listdir(origin_dir)
                )
            )
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(
                partial(self.write_composite, target_dir),
                self.emit()
            )
