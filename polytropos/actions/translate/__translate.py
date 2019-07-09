import logging
from dataclasses import dataclass
import os
import json
from typing import TYPE_CHECKING, Optional
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.actions.translate import Translator
from polytropos.util.config import MAX_WORKERS
from polytropos.util.exceptions import ExceptionWrapper

if TYPE_CHECKING:
    from polytropos.ontology.paths import PathLocator

@dataclass
class Translate(Step):
    target_schema: Schema
    translate_immutable: Translator
    translate_temporal: Translator

    """Wrapper around the tranlation functions to be used in the tasks"""

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, path_locator: "PathLocator", schema: Schema, target_schema: str):
        """
        :param path_locator:
        :param schema: The source schema, already instantiated.
        :param target_schema: The path to the definition of the target schema.
        :return:
        """
        logging.info("Initializing Translate step.")
        target_schema_instance: Schema = Schema.load(target_schema, source_schema=schema, path_locator=path_locator)
        translate_immutable: Translator = Translator(target_schema_instance.immutable)
        translate_temporal: Translator = Translator(target_schema_instance.temporal)
        return cls(target_schema_instance, translate_immutable, translate_temporal)

    def process_composite(self, origin_dir: str, target_dir: str, filename: str) -> Optional[ExceptionWrapper]:
        logging.debug('Translating composite "%s".' % filename)
        try:
            if filename.startswith("."):
                logging.info('Skipping hidden file "%s"' % filename)
                return None
            if not filename.endswith(".json"):
                logging.info('Skipping non-JSON file "%s"' % filename)
                return None

            translated = {}
            with open(os.path.join(origin_dir, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                for key, value in composite.items():
                    if key.isdigit():
                        translated[key] = self.translate_temporal(value)
                    elif key == 'immutable':
                        translated[key] = self.translate_immutable(value)
                    else:
                        pass
            with open(os.path.join(target_dir, filename), 'w') as target_file:
                json.dump(translated, target_file, indent=2)
        except Exception as e:
            logging.error("Error translating composite %s." % filename)
            return ExceptionWrapper(e)
        return None

    def __call__(self, origin_dir: str, target_dir: str):
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(
                partial(self.process_composite, origin_dir, target_dir),
                os.listdir(origin_dir)
            )
            # TODO: Exceptions are supposed to propagate from a ProcessPoolExecutor. Why aren't mine?
            for result in results:  # type: ExceptionWrapper
                if result is not None:
                    result.re_raise()
