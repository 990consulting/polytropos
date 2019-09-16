import os
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Any, Iterable, Tuple, TYPE_CHECKING, Type
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from polytropos.ontology.composite import Composite

from polytropos.actions.step import Step
from polytropos.util.loader import load
from polytropos.util.paths import find_all_composites, relpath_for

if TYPE_CHECKING:
    from polytropos.ontology.context import Context
    from polytropos.ontology.schema import Schema

@dataclass
class Scan(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
    schema: "Schema"

    """Scan iterates through all of the composites in the task pipeline twice: once to gather global information, and
    then a second time to make alterations to the composites on the basis of the globally gathered information. In
    between, an arbitrary analysis may be performed on the basis of the global information. Example use cases include
    assigning ranks, or computing a property relative to peers sharing some other property."""

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, context: "Context", schema: "Schema", name: str, mappings: Dict):  # type: ignore # Signature of "build" incompatible with supertype "Step"
        scan_subclasses: Dict[str, Type] = load(cls)
        instance_subclass: Type = scan_subclasses[name]
        return instance_subclass(**mappings, schema=schema)

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
    def alter(self, composite_id: str, composite: Composite) -> None:
        """Alter the supplied composite in place. The resulting composite will then overwrite the original, completing
        the alteration."""
        pass

    def process_composite(self, origin_dir: str, composite_id: str) -> Tuple[str, Optional[Any]]:
        relpath: str = relpath_for(composite_id)
        with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
            content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.schema, content, composite_id=composite_id)
            return composite_id, self.extract(composite)

    def alter_and_write_composite(self, origin_dir: str, target_base_dir: str, composite_id: str) -> None:
        relpath: str = relpath_for(composite_id)
        with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
            content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.schema, content, composite_id=composite_id)
            self.alter(composite_id, composite)
        target_dir: str = os.path.join(target_base_dir, relpath)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "%s.json" % composite_id), 'w') as target_file:
            json.dump(composite.content, target_file, indent=2)

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        with ThreadPoolExecutor() as executor:
            self.analyze(
                executor.map(
                    partial(self.process_composite, origin_dir),
                    find_all_composites(origin_dir)
                )
            )
        with ThreadPoolExecutor() as executor:
            executor.map(
                partial(self.alter_and_write_composite, origin_dir, target_dir),
                find_all_composites(origin_dir)
            )
