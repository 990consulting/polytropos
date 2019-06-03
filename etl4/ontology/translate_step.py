import traceback
import logging
from dataclasses import dataclass
import os
import json
from abc import abstractmethod
from collections.abc import Callable
from typing import Dict, Optional, Any, Iterable, Tuple

from etl4.ontology.step import Step
from etl4.ontology.schema import Schema
from etl4.transform.translate import Translate


@dataclass
class TranslateStep(Step):
    target_schema: Schema
    # TODO: Better typing, Callable??
    translate_invariant: Any
    translate_temporal: Any

    """Wrapper around the tranlation functions to be used in the tasks"""

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, path_locator, schema, target_schema):
        logging.info(" Loading translation step parameters from disk.")
        target_schema = Schema.load(path_locator, target_schema, schema)
        logging.info("  Initializing static variable translator.")
        translate_invariant = Translate(target_schema.invariant)
        logging.info("  Initializing temporal variable translator.")
        translate_temporal = Translate(target_schema.temporal)
        return cls(target_schema, translate_invariant, translate_temporal)

    def __call__(self, origin, target):
        logging.info("Beginning translation to %s." % self.target_schema)

        # TODO This block needs to be factored and tested
        for filename in os.listdir(origin):
            try:
                if not filename.lower().endswith(".json"):
                    logging.warning("Skipping translation for non-JSON file %s." % filename)
                    continue
                logging.debug("Translating %s." % filename)
                origin_fn: str = os.path.join(origin, filename)
                target_fn: str = os.path.join(target, filename)

                translated = {}
                with open(origin_fn, 'r') as origin_file:
                    composite = json.load(origin_file)
                    for key, value in composite.items():
                        if key == 'invariant':
                            translated[key] = self.translate_invariant(value)
                        else:
                            translated[key] = self.translate_temporal(value)
                with open(target_fn, 'w') as target_file:
                    json.dump(translated, target_file)
            except Exception:
                logging.error("Aborting translation of %s due to the following error:" % filename)
                traceback.print_exc()
                # Attempt to cleanup any partial translation
                try:
                    # noinspection PyUnboundLocalVariable
                    os.remove(target_fn)
                except IOError:
                    continue
