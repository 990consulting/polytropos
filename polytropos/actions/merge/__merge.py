import json
import os
from typing import Any, Set, Tuple, Dict, Optional

from polytropos.util.paths import find_all_composites, relpath_for

from polytropos.actions.merge.util import merge_dicts
from polytropos.actions.step import Step
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema
import shutil

def _do_copy_all(eins: Set[str], source_dir: str, target_dir: str) -> None:
    for ein in eins:
        relpath: str = relpath_for(ein)
        source: str = "{}/{}/{}.json".format(source_dir, relpath, ein)
        target: str = "{}/{}/{}.json".format(target_dir, relpath, ein)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)


def _merge_one(ein: str, primary_dir: str, secondary_dir: str, target_dir: str) -> None:
    relpath: str = relpath_for(ein)
    primary_fn: str = os.path.join(primary_dir, relpath, "{}.json".format(ein))
    secondary_fn: str = os.path.join(secondary_dir, relpath, "{}.json".format(ein))

    with open(primary_fn) as p_fh, open(secondary_fn) as s_fh:
        primary_content: Dict = json.load(p_fh)
        secondary_content: Dict = json.load(s_fh)

    merged_content: Dict = merge_dicts(primary_content, secondary_content)

    target_fn: str = os.path.join(target_dir, relpath, "{}.json".format(ein))
    os.makedirs(os.path.dirname(target_fn), exist_ok=True)
    with open(target_fn, "w") as t_fh:
        json.dump(merged_content, t_fh, indent=2)

class Merge(Step):
    def __init__(self, context: Context, schema: Schema, secondary: str):
        self.context = context
        self.schema = schema
        self.secondary_dir = os.path.join(context.entities_input_dir, secondary)

    # noinspection PyMethodOverriding
    @classmethod
    def build(cls, *, context: Context, schema: Schema, secondary: str) -> Any:  # type: ignore
        return cls(context, schema, secondary)

    def _get_ein_sets(self, origin_dir: str) -> Tuple[Set[str], Set[str], Set[str]]:
        primary_eins: Set[str] = {ein for ein in find_all_composites(origin_dir)}
        secondary_eins: Set[str] = {ein for ein in find_all_composites(self.secondary_dir)}

        primary_only = primary_eins - secondary_eins
        secondary_only = secondary_eins - primary_eins
        common = primary_eins.intersection(secondary_eins)

        return primary_only, common, secondary_only

    def _copy_directly(self, p_only: Set[str], q_only: Set[str], primary_dir: str, target_dir: str) -> None:
        _do_copy_all(p_only, primary_dir, target_dir)
        _do_copy_all(q_only, self.secondary_dir, target_dir)

    def _merge_common(self, eins: Set[str], primary_dir: str, target_dir: str) -> None:
        for ein in eins:
            _merge_one(ein, primary_dir, self.secondary_dir, target_dir)

    def __call__(self, origin_dir: str, target_dir: str) -> None:
        primary_only, common, secondary_only = self._get_ein_sets(origin_dir)
        self._copy_directly(primary_only, secondary_only, origin_dir, target_dir)
        self._merge_common(common, origin_dir, target_dir)