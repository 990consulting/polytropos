import logging
import os
import json
from dataclasses import dataclass
from typing import Dict, List, Type, Any

from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema

from polytropos.util.loader import load
from polytropos.actions.step import Step
from polytropos.util.paths import find_all_composites, relpath_for

@dataclass
class Filter(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
    """Iterate over each composite. If the composite returns False for the "passes" method, remove it from the dataset
    completely. If it returns True, apply the "narrow" method to it, which is intended to remove data (although in
    principle it could also add it). The purpose of this kind of action is to selectively remove data that is irrelevant
    to a given analysis, particularly for the preparation of end-user datasets."""

    context: Context
    schema: Schema

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, context: Context, schema: Schema, name: str, **kwargs: Any) -> "Filter":  # type: ignore
        logging.info('Building instance of filter class "%s"' % name)
        filters = load(cls)
        filter_class = filters[name]
        return filter_class.build_filter(filter_class, context, schema, **kwargs)

    # noinspection PyMethodOverriding
    @classmethod
    def build_filter(cls, filter_class: Type, context: Context, schema: Schema, **kwargs: Any) -> "Filter":
        """Build creates a filter instance"""
        return filter_class(context=context, schema=schema, **kwargs)

    def passes(self, composite: Composite) -> bool:
        """Evaluate whether the entire Composite should be included at the next Step or not."""
        return True

    def narrow(self, composite: Composite) -> None:
        """Remove or retain specific periods."""
        pass

    def process_composites(self, composite_ids: List[str], origin_dir: str, target_base_dir: str) -> None:
        for composite_id in composite_ids:
            relpath: str = relpath_for(composite_id)
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
                composite: Composite = Composite(self.schema, content, composite_id=composite_id)
                if self.passes(composite):
                    self.narrow(composite)
                    target_dir: str = os.path.join(target_base_dir, relpath)
                    os.makedirs(target_dir, exist_ok=True)
                    with open(os.path.join(target_dir, "%s.json" % composite_id), 'w') as target_file:
                        json.dump(composite.content, target_file)

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        composites_ids = list(find_all_composites(origin_dir))
        for _ in self.context.run_in_thread_pool(self.process_composites, composites_ids, origin_dir, target_dir):
            pass
