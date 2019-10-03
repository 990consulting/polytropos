import itertools
import logging
import os
import json
from dataclasses import dataclass
from abc import abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator, Type, List

from polytropos.ontology.composite import Composite

from polytropos.actions.step import Step
from polytropos.ontology.context import Context
from polytropos.util.loader import load
from polytropos.ontology.schema import Schema
from polytropos.util.paths import find_all_composites, relpath_for

def write_composites(emissions: List[Tuple[str, Composite]], target_base_dir: str) -> None:
    for emission in emissions:
        composite_id, composite = emission
        relpath: str = relpath_for(composite_id)
        target_dir: str = os.path.join(target_base_dir, relpath)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, composite_id + '.json'), 'w') as target_file:
            json.dump(composite.content, target_file, indent=2)

@dataclass  # type: ignore # https://github.com/python/mypy/issues/5374
class Aggregate(Step):
    """Iterates over all composites following one schema, and produces a new set of composites, representing a different
    kind of entity, and following a different schema."""
    context: Context
    origin_schema: Schema
    target_schema: Schema
    id_var: str

    # noinspection PyMethodOverriding
    @classmethod
    def build(  # type: ignore # Signature of "build" incompatible with supertype "Step"
            cls, context: Context, schema: Schema, name: str, target_schema: str, id_var: str,
            **kwargs
    ):
        target_schema_instance: Optional[Schema] = Schema.load(target_schema, context.schemas_dir)
        aggregations: Dict[str, Type] = load(cls)
        return aggregations[name](context=context, origin_schema=schema, target_schema=target_schema_instance, id_var=id_var,
                                  **kwargs)

    @abstractmethod
    def extract(self, composite: Composite) -> Any:
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

    def process_composites(self, composite_ids: List[str], origin_dir: str) -> List[Tuple[str, Optional[Any]]]:
        """For each composite_id: open a composite JSON file, deserialize it into a Composite object, then extract information to be used in
        analysis."""
        result: List[Tuple[str, Optional[Any]]] = []
        for composite_id in composite_ids:
            relpath: str = relpath_for(composite_id)
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
                composite: Composite = Composite(self.origin_schema, content, composite_id=composite_id)
                result.append((composite_id, self.extract(composite)))
        return result

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        composite_ids: List[str] = list(find_all_composites(origin_dir))
        logging.info("Spawning parallel processes to extract data from each composite for aggregation.")
        per_composite_results: Iterable[Tuple[str, Optional[Any]]] = itertools.chain.from_iterable(
            self.context.run_in_process_pool(self.process_composites, composite_ids, origin_dir)
        )

        self.analyze(per_composite_results)

        logging.info("Spawning parallel processes to aggregate extracted data from each composite.")
        for _ in self.context.run_in_process_pool(write_composites, list(self.emit()), target_dir):
            pass
