import logging
import os
import json
from enum import Enum
from typing import Optional, Dict, Iterable, Tuple, Iterator, Any
from dataclasses import dataclass, field
from cachetools import cachedmethod
from cachetools.keys import hashkey
from functools import partial

from polytropos.ontology.track import Track

from polytropos.ontology.variable import Variable, VariableId


SCHEMAS_DIR = 'fixtures/conf/schemas/'

class TrackType(Enum):
    IMMUTABLE = -1
    ANY = 0
    TEMPORAL = 1

class DuplicatePathError(ValueError):
    def __init__(self, var1: "Variable", var2: "Variable"):
        self.var1 = var1
        self.var2 = var2

    def __str__(self) -> str:
        template: str = 'Variables %s and %s have the same absolute path (%s)'
        return template % (self.var1.var_id, self.var2.var_id, self.var1.absolute_path)


@dataclass(eq=False)
class Schema:
    """A schema identifies all of the temporal and immutable properties that a particular entity can have."""
    temporal: Track
    immutable: Track
    name: str = "UNSPECIFIED"
    source: Optional["Schema"] = None

    _var_id_cache: Dict = field(init=False, default_factory=dict)
    _var_path_cache: Dict = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        if self.temporal.source and self.immutable.source:
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

    def _preload_var_path_cache(self) -> None:
        logging.info("Preloading absolute path cache.")
        for track in [self.temporal, self.immutable]:  # type: Track
            for var in track.values():  # type: "Variable"
                abs_path: Tuple[str, ...] = tuple(var.absolute_path)
                if abs_path in self._var_path_cache:
                    raise DuplicatePathError(var, self._var_path_cache[abs_path])
                logging.debug("Caching %s", "/".join(abs_path))
                self._var_path_cache[abs_path] = var

    def serialize(self, path: str) -> None:
        """
        Write this schema to JSON files at the specified path.

        :param path: The directory path to which to write the schema.
        :return:
        """
        immutable_fn: str = os.path.join(path, "immutable.json")
        temporal_fn: str = os.path.join(path, "temporal.json")
        with open(immutable_fn, "w") as i_fn, open(temporal_fn, "w") as t_fn:
            temporal_json: Dict = self.temporal.dump()
            json.dump(temporal_json, t_fn, indent=2)

            immutable_json: Dict = self.immutable.dump()
            json.dump(immutable_json, i_fn, indent=2)

    @classmethod
    def load(cls, path: str, schemas_dir: str, source_schema: "Schema"=None) -> Optional["Schema"]:
        """
        Constructs a schema.

        :param path: The path to the schema that is to be loaded, relative to schemas base path.
        :param schemas_dir: Directly supply the base schemas path.
        :param source_schema: An already-loaded schema from which this schema can be translated, if applicable.
        :return:
        """
        schema_name: str = "UNSPECIFIED"
        if path is not None:
            schema_name = path.replace("/", "_")

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

        temporal_path = os.path.join(schemas_dir, path, 'temporal.json')
        immutable_path = os.path.join(schemas_dir, path, 'immutable.json')

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
    def get(self, var_id: VariableId, track_type: TrackType=TrackType.ANY) -> Optional[Variable]:
        """Retrieve a particular variable from the Schema. Optionally verify the track it came from"""
        immutable_match: Optional[Variable] = self.immutable.get(var_id)
        temporal_match: Optional[Variable] = self.temporal.get(var_id)

        if immutable_match is not None and temporal_match is not None:
            raise ValueError('Variable ID "%s" occurs in both immutable and temporal tracks' % var_id)

        if track_type == TrackType.IMMUTABLE and temporal_match is not None:
            raise ValueError('Variable id "%s" was expected to be immutable, but it is temporal' % var_id)

        if track_type == TrackType.TEMPORAL and immutable_match is not None:
            raise ValueError('Variable id "%s" was expected to be temporal, but it is immutable' % var_id)

        if temporal_match is not None:
            return temporal_match

        return immutable_match

    def _lookup(self, frozen_abs_path: Tuple[str, ...]) -> Optional[Variable]:
        if frozen_abs_path in self._var_path_cache:
            return self._var_path_cache[frozen_abs_path]

        logging.debug("Path %s not in schema. Noting that in the cache.", "/".join(frozen_abs_path))
        self._var_path_cache[frozen_abs_path] = None
        return None

    def lookup(self, abs_path: Iterable[str]) -> Optional[Variable]:
        frozen_abs_path: Tuple[str, ...] = tuple(abs_path)
        return self._lookup(frozen_abs_path)

    @cachedmethod(lambda self: self._var_id_cache, key=partial(hashkey, 'istemporal'))
    def is_temporal(self, var_id: VariableId) -> bool:
        assert not (var_id in self.temporal and var_id in self.immutable)
        if var_id in self.temporal:
            return True
        if var_id in self.immutable:
            return False
        raise ValueError("No variable called %s" % var_id)

    def __iter__(self) -> Iterator["Variable"]:
        for track in [self.temporal, self.immutable]:
            yield from track.values()

    def __eq__(self, other: Optional[Any]) -> bool:
        if not isinstance(other, Schema):
            return False
        if other.name != self.name:
            return False
        if other.temporal != self.temporal:
            return False
        if other.immutable != self.immutable:
            return False
        if other.source != self.source:
            return False
        return True
