import json
import logging
import os
from typing import Dict, List, Any, Iterator

from polytropos.ontology.composite import Composite

from polytropos.util.paths import find_all_composites, relpath_for

from polytropos.actions.step import Step

from polytropos.actions.filter.mem import InMemoryFilterIterator

from polytropos.actions.filter import Filter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

class SequentialFilter(Step):  # type: ignore # https://github.com/python/mypy/issues/5374
    def __init__(self, context: Context, schema: Schema, f_iter: InMemoryFilterIterator):
        self.f_iter = f_iter
        self.context = context
        self.schema = schema

    @classmethod
    def build(cls, context: "Context", schema: "Schema", *children: List[Dict]) -> "SequentialFilter":  # type: ignore
        filters: List[Filter] = []
        for child_spec in children:
            assert isinstance(child_spec, dict) and len(child_spec) == 1
            for class_name, kwargs in child_spec.items():  # type: str, Dict
                try:
                    the_filter: Filter = Filter.build(context=context, schema=schema, name=class_name, **kwargs)
                except Exception as e:
                    raise e
                filters.append(the_filter)
        f_iter: InMemoryFilterIterator = InMemoryFilterIterator(filters)
        return cls(context, schema, f_iter)

    def _as_composites(self, composite_ids: List[str], origin_dir: str) -> Iterator[Composite]:
        for composite_id in composite_ids:
            relpath: str = relpath_for(composite_id)
            with open(os.path.join(origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
                composite: Composite = Composite(self.schema, content, composite_id=composite_id)
                yield composite

    def process_composites(self, composite_ids: List[str], origin_dir: str, target_base_dir: str) -> None:
        composites: Iterator[Composite] = self._as_composites(composite_ids, origin_dir)
        for filtered_composite in self.f_iter(composites):
            c_id: str = filtered_composite.composite_id
            relpath: str = relpath_for(c_id)
            target_dir: str = os.path.join(target_base_dir, relpath)
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, "%s.json" % c_id), 'w') as target_file:
                json.dump(filtered_composite.content, target_file, indent=2)

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        composites_ids = list(find_all_composites(origin_dir))
        logging.info("Spawning parallel processes to perform SequentialFilter operation.")
        for _ in self.context.run_in_process_pool(self.process_composites, composites_ids, origin_dir, target_dir):
            pass
