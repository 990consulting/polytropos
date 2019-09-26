import logging
import time
from dataclasses import dataclass
import os
import json
from typing import Optional, List, Callable
from functools import partial
import traceback

from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.actions.translate import Translator
from polytropos.util.paths import find_all_composites, relpath_for
from polytropos.ontology.context import Context

@dataclass
class Translate(Step):
    context: Context
    target_schema: Schema
    translate_immutable: Translator
    translate_temporal: Translator

    """Wrapper around the tranlation functions to be used in the tasks"""

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, context: "Context", schema: Schema, target_schema: str) -> "Translate":  # type: ignore # Signature of "build" incompatible with supertype "Step"
        """
        :param context:
        :param schema: The source schema, already instantiated.
        :param target_schema: The path to the definition of the target schema.
        :return:
        """
        logging.info("Initializing Translate step.")
        target_schema_instance: Optional[Schema] = Schema.load(target_schema, context.schemas_dir, source_schema=schema)
        assert target_schema_instance is not None
        translate_immutable: Translator = Translator(target_schema_instance.immutable)
        translate_temporal: Translator = Translator(target_schema_instance.temporal)
        return cls(context, target_schema_instance, translate_immutable, translate_temporal)

    def process_composite(self, origin_dir: str, target_base_dir: str, composite_id: str) -> None:
        logging.debug('Translating composite "%s".' % composite_id)
        relpath: str = relpath_for(composite_id)
        try:
            translated = {}
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                composite = json.load(origin_file)
                for key, value in composite.items():
                    if key.isdigit():
                        translated[key] = self.translate_temporal(composite_id, key, value)
                    elif key == 'immutable':
                        translated[key] = self.translate_immutable(composite_id, key, value)
                    else:
                        pass
            target_dir: str = os.path.join(target_base_dir, relpath)
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, "%s.json" % composite_id), 'w') as target_file:
                json.dump(translated, target_file, indent=2)
        except Exception as e:
            logging.error("Error translating composite %s." % composite_id)
            traceback.print_exc()
            raise

    def process_composites(self, origin_dir: str, target_dir: str, chunk: List[str]) -> None:
        start: float = time.time()
        for composite_id in chunk:
            self.process_composite(origin_dir, target_dir, composite_id)
        elapsed: float = time.time() - start
        logging.info("Completed batch of {:,} translations in {:0.2f} seconds.".format(len(chunk), elapsed))

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        composites: List[str] = list(find_all_composites(origin_dir))
        action: Callable = partial(self.process_composites, origin_dir, target_dir)
        for _ in self.context.run_in_process_pool(action, composites):
            pass
