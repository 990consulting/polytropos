import logging
from copy import deepcopy
import json
from typing import Iterator, Dict, TYPE_CHECKING, Any, Iterable, Optional
from collections.abc import MutableMapping
from polytropos.ontology.variable import (
    build_variable,
    Primitive, Container, GenericList, Validator,
    List, NamedList, Variable
)
from cachetools import cachedmethod
from cachetools.keys import hashkey
from functools import partial
import time

if TYPE_CHECKING:
    from polytropos.ontology.variable import Variable

class Track(MutableMapping):
    """Represents a hierarchy of variables associated with a particular aspect (stage) of a particular entity type, and
    that have the same temporality. That is, for every entity type, there is a temporal track and an immutable track,
    which are structured identically. The two tracks interact during the Analysis step in the generation of this entity
    type's data."""

    def __init__(self, variables: Dict[str, "Variable"], source: Optional["Track"], name: str):
        """Do not call directly; use Track.build()."""
        self._variables: Dict[str, "Variable"] = variables
        self.name = name
        self.source = source
        self.target = None
        self.schema = None
        self._cache = {}
        if source:
            source.target = self

    ###########################################
    # Mapping methods

    def __getitem__(self, key: str) -> Variable:
        return self._variables[key]

    def __setitem__(self, key: str, value: Variable) -> None:
        self._variables[key] = value

    def __delitem__(self, key: str) -> None:
        del self._variables[key]

    def __len__(self):
        return len(self._variables)

    def __iter__(self):
        return self._variables.__iter__()

    ###########################################

    @classmethod
    def build(cls, specs: Dict, source: Optional["Track"], name: str):
        """Convert specs into a Variable hierarchy, then construct a Track instance.

        :param specs: The specifications for the variables in this track.

        :param source: The source track, if any, for this track--i.e., the track corresponding to this one in the aspect
         (stage) of the analysis process that precedes this one for the particular entity type represented.

        :param name: The name of the stage/aspect."""
        logging.info("Building variables for track '%s'." % name)
        built_vars: Dict[str, "Variable"] = {}
        n: int = 0
        for variable_id, variable_data in specs.items():
            logging.debug('Building variable "%s".' % variable_id)
            variable: "Variable" = build_variable(variable_data)
            built_vars[variable_id] = variable
            n += 1
            if n % 100 == 0:
                logging.info("Built %i variables." % n)
        logging.info('Finished building all %i variables for track "%s".' % (n, name))

        track: "Track" = cls(built_vars, source, name)

        logging.info("Assigning track callbacks to variables.")
        n = 0
        for variable_id, variable in track.items():
            variable.set_track(track)
            variable.set_id(variable_id)
            n += 1
            if n % 100 == 0:
                logging.info("Assigned callbacks to %i variables." % n)
        logging.info("Assigned callbacks to all %i variables." % n)

        # we only validate after the whole thing is built to be able to
        # accurately compute siblings, parents and children
        track.invalidate_variables_cache()

        n = 0
        if name.startswith("nonprofit_origin"):
            logging.warning("Skipping validation for nonprofit origin. THIS IS DANGEROUS DEBUG LOGIC--REMOVE LATER.")
        else:
            logging.info('Performing post-load validation on variables for track "%s".' % name)
            for variable in track.values():
                Validator.validate(variable, init=True)
                n += 1
                if n % 100 == 0:
                    logging.info("Validated %i variables." % n)
            logging.info('All variables valid "%s".' % name)

        return track

    @property
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'root'))
    def roots(self) -> Iterator["Variable"]:
        """All the roots of this track's variable tree."""
        return list(filter(
            lambda variable: variable.parent == '',
            self._variables.values()
        ))

    def invalidate_variables_cache(self):
        logging.debug("Invalidating cache for all variables.")
        for variable in self._variables.values():
            variable.invalidate_cache()
        self.invalidate_cache()

    def invalidate_cache(self):
        logging.debug("Invalidating track cache.")
        self._cache.clear()
        if self.schema:
            self.schema.invalidate_cache()

    def new_var_id(self):
        """If no ID is supplied, use <stage name>_<temporal|invarant>_<n+1>,
        where n is the number of variables."""
        # Missing the temporal/immutable part for now
        return '{}_{}'.format(self.name, len(self._variables) + 1)

    def add(self, spec: Dict, var_id: str=None) -> None:
        """Validate, create, and then insert a new variable into the track."""
        if var_id is None:
            var_id = self.new_var_id()
        if var_id in self._variables:
            # Duplicated var id
            raise ValueError
        if var_id == '':
            # Invalid var id
            raise ValueError
        variable = build_variable(spec)
        variable.set_track(self)
        variable.set_id(var_id)
        Validator.validate(variable, init=True, adding=True)
        variable.update_sort_order(None, variable.sort_order)
        self._variables[var_id] = variable
        self.invalidate_variables_cache()

    def duplicate(self, source_var_id: str, new_var_id: str=None):
        """Creates a duplicate of a node, including its sources, but not including its targets."""
        if new_var_id is None:
            new_var_id = self.new_var_id()
        if new_var_id in self._variables:
            raise ValueError
        self._variables[new_var_id] = deepcopy(self._variables[source_var_id])
        self.invalidate_variables_cache()

    def delete(self, var_id: str) -> None:
        """Attempts to delete a node. Fails if the node has children or targets"""
        if var_id not in self._variables:
            raise ValueError
        variable = self._variables[var_id]
        variable.update_sort_order(variable.sort_order, None)
        if any(variable.children) or variable.has_targets:
            raise ValueError
        del self._variables[var_id]
        self.invalidate_variables_cache()

    def move(self, var_id: str, parent_id: Optional[str], sort_order: int):
        """Attempts to change the location of a node within the tree. If parent_id is None, it moves to root."""
        variable = self._variables[var_id]
        parent_id = parent_id or ''
        if parent_id and parent_id not in self._variables:
            raise ValueError
        if parent_id and variable.check_ancestor(parent_id):
            raise ValueError
        old_parent = variable.parent
        old_descends_from_list = variable.descends_from_list
        variable.update_sort_order(variable.sort_order, None)
        variable.parent = parent_id
        if variable.descends_from_list != old_descends_from_list:
            variable.parent = old_parent
            raise ValueError
        variable.update_sort_order(None, sort_order)
        variable.sort_order = sort_order
        self.invalidate_variables_cache()

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0, inside_list: int=0) \
            -> Iterator[str]:
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
