import os
import json
from polytropos.ontology.track import Track
from dataclasses import dataclass

SCHEMAS_DIR = 'fixtures/conf/schemas/'

@dataclass
class Schema:
    """A schema identifies all of the temporal and invariant properties that a particular entity can have."""
    temporal: Track
    invariant: Track

    def get(self, var_id):
        if var_id in self.invariant.variables:
            return self.invariant.variables[var_id]
        return self.temporal.variables[var_id]

    @classmethod
    def load(cls, path_locator, path, source_schema=None):
        if path is None:
            return None
        source_invariant = source_schema.invariant if source_schema else None
        source_temporal = source_schema.temporal if source_schema else None
        with open(
                os.path.join(path_locator.schemas_dir, path, 'temporal.json'), 'r'
        ) as temporal:
            with open(
                    os.path.join(path_locator.schemas_dir, path, 'invariant.json'), 'r'
            ) as invariant:
                return cls(
                    temporal=Track.build(
                        specs=json.load(temporal), source=source_temporal, name='temporal'
                    ),
                    invariant=Track.build(
                        specs=json.load(invariant), source=source_invariant, name='invariant'
                    )
                )
