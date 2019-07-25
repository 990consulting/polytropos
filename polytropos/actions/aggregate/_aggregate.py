import os
import json
from dataclasses import dataclass
from abc import abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator, Type, List as ListType
from concurrent import futures
from functools import partial

from polytropos.ontology.composite import Composite

from polytropos.actions.step import Step
from polytropos.ontology.paths import PathLocator
from polytropos.util.loader import load
from polytropos.ontology.schema import Schema

def write_composite(target_dir: str, emission: Composite):
    filename, composite = emission
    with open(os.path.join(target_dir, filename + '.json'), 'w') as target_file:
        json.dump(composite.content, target_file, indent=2)

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
        """Iterate over the extracts from each composite, performing any global processing needed and storing the
        results in instance variables.

        :param extracts: Tuple of (composite id, whatever is returned by extract)"""
        pass

    @abstractmethod
    def emit(self) -> Iterator[Tuple[str, Composite]]:
        """Lazily produce instances of the target entity. Yields tuples of (new entity ID, new entity composite)."""
        pass

    def process_composite(self, origin_dir: str, filename: str) -> Tuple[str, Optional[Any]]:
        """Open a composite JSON file, deserialize it into a Composite object, then extract information to be used in
        analysis."""
        with open(os.path.join(origin_dir, filename), 'r') as origin_file:
            content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.origin_schema, content)
            return filename, self.extract(composite)

    def __call__(self, origin_dir: str, target_dir: str):
        # References:
        #    * https://docs.python.org/3/library/concurrent.futures.html
        #    * _Fluent Python_ 1st ed, p. 547
        with futures.ThreadPoolExecutor() as executor:
            json_file_paths: ListType[str] = os.listdir(origin_dir)
            future_to_file_path: Dict = {}
            for file_path in json_file_paths:
                future = executor.submit(self.process_composite, origin_dir, file_path)
                future_to_file_path[future] = file_path
            per_composite_futures: Iterable[futures.Future] = futures.as_completed(future_to_file_path)

            per_composite_results: Iterable[Tuple[str, Optional[Any]]] = \
                (future.result() for future in per_composite_futures)

            self.analyze(per_composite_results)

        with futures.ThreadPoolExecutor() as executor:
            executor.map(
                partial(write_composite, target_dir),
                self.emit()
            )
