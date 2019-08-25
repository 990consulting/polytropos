import logging
from dataclasses import dataclass
import os
import json
from typing import TYPE_CHECKING, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.actions.translate import Translator
from polytropos.util.exceptions import ExceptionWrapper
from polytropos.util.paths import find_all_composites, relpath_for

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
    def build(cls, path_locator: "PathLocator", schema: Schema, target_schema: str) -> "Translate":  # type: ignore # Signature of "build" incompatible with supertype "Step"
        """
        :param path_locator:
        :param schema: The source schema, already instantiated.
        :param target_schema: The path to the definition of the target schema.
        :return:
        """
        logging.info("Initializing Translate step.")
        target_schema_instance: Optional[Schema] = Schema.load(target_schema, source_schema=schema, path_locator=path_locator)
        assert target_schema_instance is not None
        translate_immutable: Translator = Translator(target_schema_instance.immutable)
        translate_temporal: Translator = Translator(target_schema_instance.temporal)
        return cls(target_schema_instance, translate_immutable, translate_temporal)

    def process_composite(self, origin_dir: str, target_base_dir: str, composite_id: str) -> Optional[ExceptionWrapper]:
        logging.debug('Translating composite "%s".' % composite_id)
        relpath: str = relpath_for(composite_id)
        try:
            translated = {}
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                composite = json.load(origin_file)
                for key, value in composite.items():
                    if key.isdigit():
                        translated[key] = self.translate_temporal(value)
                    elif key == 'immutable':
                        translated[key] = self.translate_immutable(value)
                    else:
                        pass
            target_dir: str = os.path.join(target_base_dir, relpath)
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, "%s.json" % composite_id), 'w') as target_file:
                json.dump(translated, target_file, indent=2)
        except Exception as e:
            logging.error("Error translating composite %s." % composite_id)
            return ExceptionWrapper(e)
        return None

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        with ThreadPoolExecutor() as executor:
            results = executor.map(
                partial(self.process_composite, origin_dir, target_dir),
                find_all_composites(origin_dir)
            )
            # TODO: Exceptions are supposed to propagate from a ProcessPoolExecutor. Why aren't mine?
            for result in results:  # type: Optional[ExceptionWrapper]
                if result is not None:
                    result.re_raise()
