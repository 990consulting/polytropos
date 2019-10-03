import itertools
import logging
import os
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Any, Tuple, List

from polytropos.ontology.composite import Composite
from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.util.loader import load
from polytropos.ontology.context import Context
from polytropos.util.paths import find_all_composites, relpath_for


@dataclass  # type: ignore # https://github.com/python/mypy/issues/5374
class Consume(Step):
    context: Context
    schema: Schema

    """Export data from a set of composites to a single file."""
    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, context: Context, schema: Schema, name: str, **kwargs):  # type: ignore # Signature of "build" incompatible with supertype "Step"
        consumes = load(cls)
        return consumes[name](context, schema, **kwargs)

    @abstractmethod
    def before(self) -> None:
        """Optional actions to be performed after the constructor runs but before starting to consume composites."""
        pass

    @abstractmethod
    def after(self) -> None:
        """Optional actions to be performed after the composites are all consumed."""

    @abstractmethod
    def extract(self, composite: Composite) -> Any:
        """Gather the information to be used in the analysis."""
        pass

    @abstractmethod
    def consume(self, extracts: Iterable[Any]) -> None:
        """Iterate over the extracts from each composite. Output may be written at this point, or data may be stored in
        instance variables for global analysis and emission in the "after()" function.

        :param extracts: List of whatever is returned by extract"""
        pass

    def process_composites_chunk(self, composite_ids: List[str], origin_dir: str) -> List[Any]:
        """For each composite_id: open a composite JSON file, deserialize it into a Composite object, then extract information to be used in
        analysis."""
        result: List[Any] = []
        for composite_id in composite_ids:
            relpath: str = relpath_for(composite_id)
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.schema, content, composite_id=composite_id)
            result.append(self.extract(composite))
        return result

    def process_composites(self, composite_ids: Iterable[str], origin_dir: str) -> Iterable[Any]:
        logging.info("Spawning parallel processes to consume composites.")
        results: Iterable[List[Any]] = self.context.run_in_thread_pool(self.process_composites_chunk, list(composite_ids), origin_dir)
        return itertools.chain.from_iterable(results)

    def __call__(self, origin_dir: str, target_dir: Optional[str]) -> None:
        """Generate the export file."""
        self.before()
        composite_ids: Iterable[str] = find_all_composites(origin_dir)
        per_composite_results: Iterable[Any] = self.process_composites(composite_ids, origin_dir)

        self.consume(per_composite_results)
        self.after()
