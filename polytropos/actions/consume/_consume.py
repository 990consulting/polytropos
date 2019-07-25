import logging
import os
import json
from abc import abstractmethod
from dataclasses import dataclass
from concurrent import futures
from typing import List as ListType, Dict, Iterable, Optional, Any, Tuple

from polytropos.ontology.composite import Composite
from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.util.loader import load
from polytropos.ontology.paths import PathLocator


@dataclass
class Consume(Step):
    path_locator: PathLocator
    schema: Schema

    """Export data from a set of composites to a single file."""
    @classmethod
    def build(cls, path_locator: PathLocator, schema: Schema, name: str, **kwargs):
        consumes = load(cls)
        return consumes[name](path_locator, schema, **kwargs)

    @abstractmethod
    def before(self):
        """Optional actions to be performed after the constructor runs but before starting to consume composites."""
        pass

    @abstractmethod
    def after(self):
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

    def process_composite(self, origin_dir: str, filename: str):
        """Open a composite JSON file, deserialize it into a Composite object, then extract information to be used in
        analysis."""
        with open(os.path.join(origin_dir, filename), 'r') as origin_file:
            content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.schema, content)
            return filename, self.extract(composite)

    def __call__(self, origin_dir: str, target_dir: str):
        """Generate the export file."""
        self.before()
        with futures.ThreadPoolExecutor() as executor:
            json_file_paths: ListType[str] = os.listdir(origin_dir)
            future_to_file_path: Dict = {}
            for file_path in json_file_paths:
                if not file_path.endswith(".json"):
                    logging.warning("Skipping non-JSON file %s" % file_path)
                    continue
                future = executor.submit(self.process_composite, origin_dir, file_path)
                future_to_file_path[future] = file_path

            per_composite_futures: Iterable[futures.Future] = futures.as_completed(future_to_file_path)

            per_composite_results: Iterable[Tuple[str, Optional[Any]]] = \
                (future.result() for future in per_composite_futures)

            self.consume(per_composite_results)

        self.after()


