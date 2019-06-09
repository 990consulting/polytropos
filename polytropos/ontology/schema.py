import os
import json
from enum import Enum
from typing import Optional

from polytropos.ontology.track import Track
from dataclasses import dataclass

from polytropos.ontology.variable import Variable

SCHEMAS_DIR = 'fixtures/conf/schemas/'

class TrackType(Enum):
    IMMUTABLE = -1
    ANY = 0
    TEMPORAL = 1

@dataclass
class Schema:
    """A schema identifies all of the temporal and immutable properties that a particular entity can have."""
    temporal: Track
    immutable: Track

    # TODO Add caching and validation that both update on load and mutate
    def get(self, var_id: str, track_type: TrackType=TrackType.ANY) -> Optional[Variable]:
        """Retrieve a particular variable from the Schema. Optionally verify the track it came from"""
        immutable_match: Variable = self.immutable.variables.get(var_id)
        temporal_match: Variable = self.temporal.variables.get(var_id)

        if immutable_match is not None and temporal_match is not None:
            raise ValueError('Variable ID "%s" occurs in both immutable and temporal tracks' % var_id)

        if track_type == TrackType.IMMUTABLE and temporal_match is not None:
            raise ValueError('Variable id "%s" was expected to be immutable, but it is temporal' % var_id)

        if track_type == TrackType.TEMPORAL and immutable_match is not None:
            raise ValueError('Variable id "%s" was expected to be temporal, but it is immutable' % var_id)

        if temporal_match is not None:
            return temporal_match

        return immutable_match

    @classmethod
    def load(cls, path_locator, path, source_schema=None):
        if path is None:
            return None
        source_immutable = source_schema.immutable if source_schema else None
        source_temporal = source_schema.temporal if source_schema else None
        with open(
                os.path.join(path_locator.schemas_dir, path, 'temporal.json'), 'r'
        ) as temporal:
            with open(
                    os.path.join(path_locator.schemas_dir, path, 'immutable.json'), 'r'
            ) as immutable:
                return cls(
                    temporal=Track.build(
                        specs=json.load(temporal), source=source_temporal, name='temporal'
                    ),
                    immutable=Track.build(
                        specs=json.load(immutable), source=source_immutable, name='immutable'
                    )
                )
