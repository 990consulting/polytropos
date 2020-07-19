import logging
import os
import json
import time
import traceback
from collections.abc import Callable
from typing import Dict, List, TYPE_CHECKING

from polytropos.actions.evolve.__factory import _EvolveFactory
from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change
from polytropos.actions.step import Step
from polytropos.util.paths import find_all_composites, relpath_for

if TYPE_CHECKING:
    from polytropos.ontology.context import Context
    from polytropos.ontology.schema import Schema

class Evolve(Step):
    """A metamorphosis represents a series of changes that are made to a single composite, in order, and without
    reference to any other composite. Each change is defined in terms of one or more subject variables, which may be
    inputs, outputs, or both (in a case where a change alters a value in place)."""

    def __init__(self, context: "Context", changes: List[Change], schema: "Schema"):
        self.context = context
        self.changes = changes
        self.schema = schema

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, *, context: "Context", schema: "Schema", changes: List[Dict], lookups: List[str] = None) -> "Evolve":  # type: ignore # Signature of "build" incompatible with supertype "Step"
        """Loads in the specified lookup tables, constructs the specified Changes, and passes these Changes to the
        constructor.
        :param context: Helper class that finds requested files in a configuration path.
        :param changes: List of change definitions (from the task YAML file)
        :param schema: The schema on which the composites are expected to be based.
        :param lookups: A list of key-value lookups expected to be available during each Change.
        """
        do_build: Callable = _EvolveFactory(context, changes, schema, lookups)
        return do_build(cls)

    def process_composite(self, origin_dir: str, base_target_dir: str, composite_id: str) -> None:
        try:
            relpath: str = relpath_for(composite_id)
            origin_filename: str = os.path.join(origin_dir, relpath, "%s.json" % composite_id)
            logging.debug("Evolving %s." % origin_filename)
            with open(origin_filename) as origin_file:
                content: Dict = json.load(origin_file)
                composite: Composite = Composite(self.schema, content, composite_id=composite_id)
                for change in self.changes:
                    logging.debug('Applying change "%s" to %s.' % (change.__class__.__name__, origin_filename))
                    change(composite)
            target_dir: str = os.path.join(base_target_dir, relpath)
            os.makedirs(target_dir, exist_ok=True)
            target_filepath: str = os.path.join(target_dir, "%s.json" % composite_id)
            with open(target_filepath, 'w') as target_file:
                json.dump(composite.content, target_file, indent=2)
        except Exception as e:
            logging.error("Error processing composite %s during evolve step." % composite_id)
            traceback.print_exc()
            raise

    def process_composites(self, chunk: List[str], origin_dir: str, target_dir: str) -> None:
        start: float = time.time()
        for composite_id in chunk:
            self.process_composite(origin_dir, target_dir, composite_id)
        elapsed: float = time.time() - start
        logging.info("Completed batch of {:,} evolutions in {:0.2f} seconds.".format(len(chunk), elapsed))

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        composites: List[str] = list(find_all_composites(origin_dir))
        logging.info("Spawning parallel processes to perform Evolve process on all composites.")
        for _ in self.context.run_in_process_pool(self.process_composites, composites, origin_dir, target_dir):
            pass
