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
                    temporal=json.load(temporal),
                    invariant=json.load(invariant)
                )
