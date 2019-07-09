import logging
import os
import json
from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING, Iterable, Tuple, Iterator
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

class DuplicatePathError(ValueError):
    def __init__(self, var1: "Variable", var2: "Variable"):
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        template: str = 'Variables %s and %s have the same absolute path (%s)'
        return template % (self.var1.var_id, self.var2.var_id, self.var1.absolute_path)

@dataclass
class Schema:
    """A schema identifies all of the temporal and immutable properties that a particular entity can have."""
    temporal: Track
    immutable: Track
    name: str = "UNSPECIFIED"
    source: "Schema" = None

    _var_id_cache: Dict = field(init=False, default_factory=dict)
    _var_path_cache: Dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        if self.temporal.source or self.immutable.source:
            if self.temporal.source.schema is not self.immutable.source.schema:
                raise RuntimeError("Temporal and immutable tracks have different source schemas.")
            self.source = self.temporal.source.schema

        self.temporal.schema = self
        self.immutable.schema = self
        repeated = self.temporal.keys() & self.immutable.keys()
        if repeated:
            raise ValueError(
                'The variable ids intersect in {}'.format(repeated)
            )
        self._preload_var_path_cache()

    def _preload_var_path_cache(self):
        for track in [self.temporal, self.immutable]:  # type: Track
            for var in track.values():  # type: str, "Variable"
                abs_path: Tuple[str] = tuple(var.absolute_path)
                if abs_path in self._var_path_cache:
                    raise DuplicatePathError(var, self._var_path_cache[abs_path])
                self._var_path_cache[abs_path] = var

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
        # We return None if path is None to adapt to the case of a task not
        # having a target schema.
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

    @cachedmethod(lambda self: self._var_id_cache, key=partial(hashkey, 'root'))
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

    def _lookup(self, frozen_abs_path: Tuple[str]) -> Optional[Variable]:
        if frozen_abs_path in self._var_path_cache:
            return self._var_path_cache[frozen_abs_path]

        for var in self:  # type: "Variable"
            abs_path: Tuple[str] = tuple(var.absolute_path)
            if abs_path not in self._var_path_cache:
                self._var_path_cache[abs_path] = var
            if abs_path == frozen_abs_path:
                return var

    def lookup(self, abs_path: Iterable[str]) -> Optional[Variable]:
        frozen_abs_path = tuple(abs_path)
        return self._lookup(frozen_abs_path)

    def invalidate_cache(self):
        logging.info("Invalidating schema caches.")
        self._var_id_cache.clear()
        self._var_path_cache.clear()

    def __iter__(self) -> Iterator["Variable"]:
        for track in [self.temporal, self.immutable]:
            yield from track.values()
