import logging
import os
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.util.exceptions import ExceptionWrapper

from polytropos.util.loader import load
from polytropos.actions.step import Step
from polytropos.util.paths import find_all_composites, relpath_for

@dataclass
class Filter(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
    """Iterate over each composite. If the composite returns False for the "passes" method, remove it from the dataset
    completely. If it returns True, apply the "narrow" method to it, which is intended to remove data (although in
    principle it could also add it). The purpose of this kind of action is to selectively remove data that is irrelevant
    to a given analysis, particularly for the preparation of end-user datasets."""

    schema: Schema

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, context, schema: Schema, name: str, mappings: Optional[Dict] = None):  # type: ignore
        if mappings is None:
            mappings = {}
        logging.info('Building instance of filter class "%s"' % name)
        filters = load(cls)
        return filters[name](schema=schema, **mappings)

    def passes(self, composite: Composite) -> bool:
        """Evaluate whether the entire Composite should be included at the next Step or not."""
        return True

    def narrow(self, composite: Composite) -> None:
        """Remove or retain specific periods."""
        pass

    def process_composite(self, origin_dir: str, target_base_dir: str, composite_id: str) -> Optional[ExceptionWrapper]:
        relpath: str = relpath_for(composite_id)
        try:
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
                composite: Composite = Composite(self.schema, content, composite_id=composite_id)
                if self.passes(composite):
                    self.narrow(composite)
                    target_dir: str = os.path.join(target_base_dir, relpath)
                    os.makedirs(target_dir, exist_ok=True)
                    with open(os.path.join(target_dir, "%s.json" % composite_id), 'w') as target_file:
                        json.dump(composite.content, target_file)
        except Exception as e:
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
