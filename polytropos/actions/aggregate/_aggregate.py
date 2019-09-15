import os
import json
from dataclasses import dataclass
from abc import abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator, Type, List as ListType
from concurrent import futures
from functools import partial

from polytropos.ontology.composite import Composite

from polytropos.actions.step import Step
from polytropos.ontology.context import Context
from polytropos.util.loader import load
from polytropos.ontology.schema import Schema
from polytropos.util.paths import find_all_composites, relpath_for

def write_composite(target_base_dir: str, emission: Tuple[str, Composite]) -> None:
    composite_id, composite = emission
    relpath: str = relpath_for(composite_id)
    target_dir: str = os.path.join(target_base_dir, relpath)
    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, composite_id + '.json'), 'w') as target_file:
        json.dump(composite.content, target_file, indent=2)

@dataclass
class Aggregate(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
    """Iterates over all composites following one schema, and produces a new set of composites, representing a different
    kind of entity, and following a different schema."""
    origin_schema: Schema
    target_schema: Schema
    id_var: str

    # noinspection PyMethodOverriding
    @classmethod
    def build(  # type: ignore # Signature of "build" incompatible with supertype "Step"
            cls, context: Context, schema: Schema, name: str, target_schema: str, id_var: str,
            input_mappings: Dict, output_mappings: Dict
    ):
        target_schema_instance: Optional[Schema] = Schema.load(target_schema, context.schemas_dir)
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

    def process_composite(self, origin_dir: str, composite_id: str) -> Tuple[str, Optional[Any]]:
        """Open a composite JSON file, deserialize it into a Composite object, then extract information to be used in
        analysis."""
        relpath: str = relpath_for(composite_id)
        with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
            content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.origin_schema, content, composite_id=composite_id)
            return composite_id, self.extract(composite)

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        # References:
        #    * https://docs.python.org/3/library/concurrent.futures.html
        #    * _Fluent Python_ 1st ed, p. 547
        """
        composite_ids: Iterator[str] = find_all_composites(origin_dir)
        extracts = (self.process_composite(origin_dir, composite_id) for composite_id in composite_ids)
        self.analyze(extracts)
        targets = self.emit()
        for target in targets:
            write_composite(target_dir, target)
        """
        with futures.ThreadPoolExecutor() as executor:
            composite_ids: Iterator[str] = find_all_composites(origin_dir)
            future_to_composite_id: Dict = {}
            for composite_id in composite_ids:
                future = executor.submit(self.process_composite, origin_dir, composite_id)
                future_to_composite_id[future] = composite_id
            per_composite_futures: Iterable[futures.Future] = futures.as_completed(future_to_composite_id)

            per_composite_results: Iterable[Tuple[str, Optional[Any]]] = \
                (future.result() for future in per_composite_futures)

            self.analyze(per_composite_results)

        with futures.ThreadPoolExecutor() as executor:
            executor.map(
                partial(write_composite, target_dir),
                self.emit()
            )
