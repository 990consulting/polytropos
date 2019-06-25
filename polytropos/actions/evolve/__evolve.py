import logging
import os
import json
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Dict, List, Optional, TYPE_CHECKING, Type, Iterator

from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable
from polytropos.util.exceptions import ExceptionWrapper

from polytropos.util.loader import load
from polytropos.actions.evolve import Change
from polytropos.actions.step import Step
from polytropos.util.config import MAX_WORKERS

if TYPE_CHECKING:
    from polytropos.ontology.paths import PathLocator
    from polytropos.ontology.schema import Schema

class _EvolveFactory(Callable):
    def __init__(self, path_locator: "PathLocator",
                 change_specs: List[Dict],
                 schema: "Schema",
                 requested_lookups: Optional[List[str]]):

        self.change_classes: Dict[str, Type] = load(Change)
        self.requested_lookups: List[str] = requested_lookups or []
        self.change_specs: List[Dict] = change_specs
        self.schema: "Schema" = schema
        self.path_locator: "PathLocator" = path_locator

    def _load_lookups(self) -> Dict[str, Dict]:
        loaded_lookups: Dict = {}
        lookups = self.requested_lookups
        for lookup in lookups:
            with open(os.path.join(self.path_locator.lookups_dir, lookup + '.json'), 'r') as l:
                loaded_lookups[lookup] = json.load(l)
        return loaded_lookups

    def _construct_change(self, class_name: str, mappings: Dict[str, str], loaded_lookups: Dict[str, Dict]) -> Change:
        change_class: Type = self.change_classes[class_name]
        change: Change = change_class(
            **mappings, schema=self.schema, lookups=loaded_lookups
        )
        return change

    def _construct_changes(self, loaded_lookups: Dict[str, Dict]) -> Iterator[Change]:
        for spec in self.change_specs:
            assert len(spec) == 1, "Malformed change specification"
            for class_name, var_specs in spec.items():
                change: Change = self._construct_change(class_name, var_specs, loaded_lookups)
                yield change

    def __call__(self, cls: Type) -> "Evolve":
        loaded_lookups: Dict[str, Dict] = self._load_lookups()
        change_instances: List[Change] = list(self._construct_changes(loaded_lookups))
        return cls(self.path_locator, change_instances, self.schema)

class Evolve(Step):
    """A metamorphosis represents a series of changes that are made to a single composite, in order, and without
    reference to any other composite. Each change is defined in terms of one or more subject variables, which may be
    inputs, outputs, or both (in a case where a change alters a value in place)."""

    def __init__(self, path_locator: "PathLocator", changes: List[Change], schema: "Schema"):
        self.path_locator = path_locator
        self.changes = changes
        self.schema = schema

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, *, path_locator: "PathLocator", schema: "Schema", changes: List[Dict], lookups: List[str]=None) -> "Evolve":
        """Loads in the specified lookup tables, constructs the specified Changes, and passes these Changes to the
        constructor.
        :param path_locator: Helper class that finds requested files in a configuration path.
        :param changes: List of change definitions (from the task YAML file)
        :param schema: The schema on which the composites are expected to be based.
        :param lookups: A list of key-value lookups expected to be available during each Change.
        """
        do_build: Callable = _EvolveFactory(path_locator, changes, schema, lookups)
        return do_build(cls)

    def process_composite(self, origin, target, filename) -> Optional[ExceptionWrapper]:
        try:
            origin_filename: str = os.path.join(origin, filename)
            logging.debug("Evolving %s." % origin_filename)
            with open(origin_filename, 'r') as origin_file:
                content: Dict = json.load(origin_file)
                composite_id: str = filename[:-5]
                composite: Composite = Composite(self.schema, content, composite_id=composite_id)
                for change in self.changes:
                    logging.debug('Applying change "%s" to %s.' % (change.__class__.__name__, origin_filename))
                    change(composite)
            with open(os.path.join(target, filename), 'w') as target_file:
                json.dump(composite.content, target_file, indent=2)
        except Exception as e:
            return ExceptionWrapper(e)
        return None

    def __call__(self, origin_dir, target_dir):
        targets = os.listdir(origin_dir)
        logging.debug("I have the following targets:\n   - %s" % "\n   - ".join(targets))
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(
                partial(self.process_composite, origin_dir, target_dir),
                targets
            )
            # TODO: Exceptions are supposed to propagate from a ProcessPoolExecutor. Why aren't mine?
            for result in results:  # type: ExceptionWrapper
                if result is not None:
                    result.re_raise()
