import os
import json
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Dict, List

from polytropos.util.loader import load
# TODO Find out how to avoid needing to do this kind of thing
from polytropos.actions.evolve.__change import Change
from polytropos.actions.step import Step
from polytropos.util.config import MAX_WORKERS


class Evolve(Step):
    """A metamorphosis represents a series of changes that are made to a single composite, in order, and without
    reference to any other composite. Each change is defined in terms of one or more subject variables, which may be
    inputs, outputs, or both (in a case where a change alters a value in place)."""

    def __init__(self, path_locator, changes, schema, lookups):
        self.path_locator = path_locator
        self.changes = changes
        self.lookups = lookups
        self.schema = schema

    @classmethod
    def build(cls, path_locator, changes, schema, lookups=None) -> "Evolve":
        """Loads in the specified lookup tables, constructs the specified Changes, and passes these Changes to the
        constructor."""
        loaded_lookups = {}
        lookups = lookups or []
        for lookup in lookups:
            with open(os.path.join(path_locator.lookups_dir, lookup + '.json'), 'r') as l:
                loaded_lookups[lookup] = json.load(l)
        change_instances = []
        all_changes = load(Change)
        for spec in changes:
            # assume that spec only has one key
            assert len(spec) == 1
            for name, var_specs in spec.items():
                variables = {
                    var_name: schema.get(var_id)
                    for var_name, var_id in var_specs.items()
                }
                change = all_changes[name](
                    **variables, lookups=loaded_lookups, schema=schema
                )
                change_instances.append(change)
        return cls(path_locator, change_instances, lookups, schema)

    def process_composite(self, origin, target, filename):
        with open(os.path.join(origin, filename), 'r') as origin_file:
            composite = json.load(origin_file)
            for change in self.changes:
                change(composite)
        with open(os.path.join(target, filename), 'w') as target_file:
            json.dump(composite, target_file)

    def __call__(self, origin, target):
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(
                partial(self.process_composite, origin, target),
                os.listdir(origin)
            )
