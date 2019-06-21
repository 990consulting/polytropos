import logging
import os
import json
from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING
from dataclasses import dataclass, field
from cachetools import cachedmethod
from cachetools.keys import hashkey
from functools import partial

from polytropos.ontology.track import Track

from polytropos.ontology.variable import Variable

if TYPE_CHECKING:
    from polytropos.ontology.paths import PathLocator

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
    name: str = "UNSPECIFIED"

    _cache: Dict = field(init=False, default_factory=dict)

    @classmethod
    def load(cls, path_locator: "PathLocator", path: str, source_schema: "Schema"=None):
        """
        Constructs a schema.

        :param path_locator: Utility class that resolves file paths based on Polytropos' configuration base path.
        :param path: The path to the schema that is to be loaded, relative to schemas base path.
        :param source_schema: An already-loaded schema from which this schema can be translated, if applicable.
        :return:
        """
        schema_name = "UNSPECIFIED"
        if path is not None:
            schema_name: str = path.replace("/", "_")

        logging.info('Loading schema "%s".' % schema_name)
        # TODO Figure out why these two lines are necessary. They definitely are, for now.
        if path is None:
            return None

        if source_schema:
            logging.debug('Schema "%s" has source schema "%s".' % (schema_name, source_schema.name))
        else:
            logging.debug('Schema "%s" has no source schema.' % schema_name)

        source_immutable: Optional[Track] = source_schema.immutable if source_schema else None
        source_temporal: Optional[Track] = source_schema.temporal if source_schema else None

        temporal_path: str = os.path.join(path_locator.schemas_dir, path, 'temporal.json')
        immutable_path: str = os.path.join(path_locator.schemas_dir, path, 'immutable.json')

        logging.debug('Temporal path for schema "%s": %s' % (schema_name, temporal_path))
        logging.debug('Immutable path for schema "%s": %s' % (schema_name, temporal_path))

        with open(temporal_path, 'r') as temporal, open(immutable_path, 'r') as immutable:
            return cls(
                temporal=Track.build(
                    specs=json.load(temporal), source=source_temporal, name='%s_temporal' % schema_name
                ),
                immutable=Track.build(
                    specs=json.load(immutable), source=source_immutable, name='%s_immutable' % schema_name
                ),
                name=schema_name
            )

    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'root'))
    def get(self, var_id: str, track_type: TrackType=TrackType.ANY) -> Optional[Variable]:
        """Retrieve a particular variable from the Schema. Optionally verify the track it came from"""
        immutable_match: Variable = self.immutable.get(var_id)
        temporal_match: Variable = self.temporal.get(var_id)

        if immutable_match is not None and temporal_match is not None:
            raise ValueError('Variable ID "%s" occurs in both immutable and temporal tracks' % var_id)

        if track_type == TrackType.IMMUTABLE and temporal_match is not None:
            raise ValueError('Variable id "%s" was expected to be immutable, but it is temporal' % var_id)

        if track_type == TrackType.TEMPORAL and immutable_match is not None:
            raise ValueError('Variable id "%s" was expected to be temporal, but it is immutable' % var_id)

        if temporal_match is not None:
            return temporal_match

        return immutable_match

    def __post_init__(self):
        self.temporal.schema = self
        self.immutable.schema = self

    def invalidate_cache(self):
        logging.info("Invalidating schema cache.")
        self._cache.clear()

