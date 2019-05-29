import os
import json
from typing import Dict, List
from etl4.ontology.metamorphosis.__change import load_changes


class Metamorphosis:
    """A metamorphosis represents a series of changes that are made to a single composite, in order, and without
    reference to any other composite. Each change is defined in terms of one or more subject variables, which may be
    inputs, outputs, or both (in a case where a change alters a value in place)."""

    def __init__(self, path_locator, changes, lookups, schema):
        self.path_locator = path_locator
        self.changes = changes
        self.lookups = lookups
        self.schema = schema

    @classmethod
    def build(cls, path_locator, changes, lookups, schema) -> "Metamorphosis":
        """Loads in the specified lookup tables, constructs the specified Changes, and passes these Changes to the
        constructor."""
        loaded_lookups = {}
        for lookup in lookups:
            with open(os.path.join(path_locator.lookups_dir, lookup + '.json'), 'r') as l:
                loaded_lookups[lookup] = json.load(l)
        change_instances = []
        all_changes = load_changes(path_locator)
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

    def __call__(self, composite: Dict) -> None:
        for change in self.changes:
            change(composite)
