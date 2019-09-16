import logging
import os
import json
from abc import abstractmethod
from dataclasses import dataclass
from concurrent import futures
from typing import List as ListType, Dict, Iterable, Optional, Any, Tuple, List

from polytropos.ontology.composite import Composite
from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.util.loader import load
from polytropos.ontology.context import Context
from polytropos.util.paths import find_all_composites, relpath_for
from multiprocessing import cpu_count

@dataclass
class Consume(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
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
    def extract(self, composite: Composite) -> Optional[Any]:
        """Gather the information to be used in the analysis."""
        pass

    @abstractmethod
    def consume(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        """Iterate over the extracts from each composite. Output may be written at this point, or data may be stored in
        instance variables for global analysis and emission in the "after()" function.

        :param extracts: Tuple of (composite filename, whatever is returned by extract)"""
        pass

    def process_composite(self, composite_id: str, origin_dir: str) -> Tuple[str, Optional[Any]]:
        """Open a composite JSON file, deserialize it into a Composite object, then extract information to be used in
        analysis."""
        relpath: str = relpath_for(composite_id)
        with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
            content: Dict = json.load(origin_file)
        composite: Composite = Composite(self.schema, content, composite_id=composite_id)
        return composite_id, self.extract(composite)

    # noinspection PyMethodMayBeStatic
    def _get_executor(self, *args: Any, **kwargs: Any) -> futures.Executor:
        return futures.ThreadPoolExecutor()

    def process_composites(self, composite_ids: Iterable[str], origin_dir: str) -> Iterable[Tuple[str, Optional[Any]]]:
        # yield from (self.process_composite(composite_id, origin_dir) for composite_id in composite_ids)
        with self._get_executor() as executor:
            future_to_file_path: Dict = {}
            for composite_id in composite_ids:
                future = executor.submit(self.process_composite, composite_id, origin_dir)
                future_to_file_path[future] = composite_id

            per_composite_futures: Iterable[futures.Future] = futures.as_completed(future_to_file_path)

        yield from (future.result() for future in per_composite_futures)

    def __call__(self, origin_dir: str, target_dir: Optional[str]) -> None:
        """Generate the export file."""
        self.before()
        composite_ids: Iterable[str] = find_all_composites(origin_dir)
        per_composite_results: Iterable[Tuple[str, Any]] = self.process_composites(composite_ids, origin_dir)

        self.consume(per_composite_results)
        self.after()
