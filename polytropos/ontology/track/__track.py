import logging
import json
from typing import Iterator, Dict, TYPE_CHECKING, Any, Optional, List as ListType, Set
from collections.abc import MutableMapping

from polytropos.ontology.variable import (
    Primitive, Container, Validator,
    Variable, VariableId
)
import polytropos.ontology.variable
from cachetools import cachedmethod
from cachetools.keys import hashkey
from functools import partial

if TYPE_CHECKING:
    from polytropos.ontology.schema import Schema


class Track(MutableMapping):
    """Represents a hierarchy of variables associated with a particular aspect (stage) of a particular entity type, and
    that have the same temporality. That is, for every entity type, there is a temporal track and an immutable track,
    which are structured identically. The two tracks interact during the Analysis step in the generation of this entity
    type's data."""

    ALLOWED_VAR_SPEC_FIELDS: Set[str] = {"name", "data_type", "sort_order", "parent", "sources", "metadata"}

    def __init__(self, specs: Dict, source: Optional["Track"], name: str):
        """Do not call directly; use Track.build()."""
        self._variables: Dict["VariableId", "Variable"] = {}
        self.name = name
        self.source = source
        self.target = None
        self.schema: Optional["Schema"] = None
        self._cache: Dict[str, Any] = {}
        if source:
            source.target = self

        logging.info("Building variables for track '%s'." % name)
        n: int = 0
        for variable_id, variable_data in specs.items():
            if variable_id == '':
                # Invalid var id
                raise ValueError

            logging.debug('Building variable "%s".' % variable_id)
            variable: "Variable" = self.build_variable(variable_data, variable_id)
            self._variables[VariableId(variable_id)] = variable
            n += 1
            if n % 100 == 0:
                logging.info("Built %i variables." % n)
        logging.info('Finished building all %i variables for track "%s".' % (n, name))

        logging.info('Performing post-load validation on variables for track "%s".' % name)
        n = 0
        for variable in self.values():
            Validator.validate(variable, init=True)
            n += 1
            if n % 100 == 0:
                logging.info("Validated %i variables.", n)
        logging.info('All variables valid "%s".' % name)

    def build_variable(self, data: Dict, var_id: VariableId) -> Variable:
        unexpected_fields = set(data.keys()).difference(Track.ALLOWED_VAR_SPEC_FIELDS)
        if len(unexpected_fields) > 0:
            raise ValueError("unexpected variable fields: %s" % sorted(unexpected_fields))

        try:
            data_type = data['data_type']
        except Exception as e:
            print("breakpoint")
            raise e
        try:
            del data['data_type']
            cls = getattr(polytropos.ontology.variable, data_type)
            var = cls(track=self, var_id=var_id, **data)
            data['data_type'] = data_type
            return var
        except Exception as e:
            print("breakpoint")
            raise e

    ###########################################
    # Mapping methods

    def __getitem__(self, key: VariableId) -> Variable:
        return self._variables[key]

    def __setitem__(self, key: "VariableId", value: Variable) -> None:
        self._variables[key] = value

    def __delitem__(self, key: "VariableId") -> None:
        del self._variables[key]

    def __len__(self) -> int:
        return len(self._variables)

    def __iter__(self) -> Iterator[VariableId]:
        return self._variables.__iter__()

    def __eq__(self, other: Optional[Any]) -> bool:
        if not isinstance(other, Track):
            return False
        if other.name != self.name:
            return False
        if other._variables != self._variables:
            return False
        return True

    ###########################################

    @classmethod
    def build(cls, specs: Dict, source: Optional["Track"], name: str) -> "Track":
        """Convert specs into a Variable hierarchy, then construct a Track instance.

        :param specs: The specifications for the variables in this track.

        :param source: The source track, if any, for this track--i.e., the track corresponding to this one in the aspect
         (stage) of the analysis process that precedes this one for the particular entity type represented.

        :param name: The name of the stage/aspect."""
        return cls(specs, source, name)

    @property  # type: ignore # Decorated property not supported
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'root'))
    def roots(self) -> ListType["Variable"]:
        """All the roots of this track's variable tree."""
        return list(filter(
            lambda variable: variable.parent is None,
            self._variables.values()
        ))

    def new_var_id(self) -> VariableId:
        """If no ID is supplied, use <stage name>_<temporal|invarant>_<n+1>,
        where n is the number of variables."""
        # Missing the temporal/immutable part for now
        return VariableId('{}_{}'.format(self.name, len(self._variables) + 1))

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0, inside_list: int=0) \
            -> Iterator[VariableId]:
        """Provides a list of variable IDs in this track that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        :param inside_list: If -1, include only elements outside lists; if 1, only inside lists.
        """
        for variable_id, variable in self._variables.items():
            if data_type is None or variable.data_type == data_type:
                if targets:
                    if targets == -1 and variable.has_targets:
                        continue
                    if targets == 1 and not variable.has_targets:
                        continue
                if container:
                    if container == -1 and not isinstance(variable, Primitive):
                        continue
                    if container == 1 and not isinstance(variable, Container):
                        continue
                if inside_list:
                    if inside_list == -1 and variable.descends_from_list:
                        continue
                    if inside_list == 1 and not variable.descends_from_list:
                        continue
                yield variable_id

    def dump(self) -> Dict:
        """A Dict representation of this track."""
        representation = {}
        for variable_id, variable in sorted(self._variables.items()):
            representation[variable_id] = variable.dump()
        return representation

    def dumps(self) -> str:
        """A pretty JSON string representation of this track."""
        return json.dumps(self.dump(), indent=2)
