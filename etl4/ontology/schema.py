import os
import json
from etl4.ontology.track import Track
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
    def load(cls, path):
        if path is None:
            return None
        with open(
                os.path.join(SCHEMAS_DIR, path, 'temporal.json'), 'r'
        ) as temporal:
            with open(
                    os.path.join(SCHEMAS_DIR, path, 'invariant.json'), 'r'
            ) as invariant:
                return cls(
                    temporal=Track.build(
                        specs=json.load(temporal), source=None, name='temporal'
                    ),
                    invariant=Track.build(
                        specs=json.load(invariant), source=None, name='invariant'
                    )
                )
