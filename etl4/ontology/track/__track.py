from copy import deepcopy
from dataclasses import asdict
import json
from typing import Iterator, Dict, TYPE_CHECKING, List, Any, Iterable, Optional
from etl4.ontology.variable import (
    build_variable, Primitive, Container, GenericList, Validator
)

if TYPE_CHECKING:
    from etl4.ontology.variable import Variable

class Track:
    """Represents a hierarchy of variables associated with a particular aspect (stage) of a particular entity type, and
    that have the same temporality. That is, for every entity type, there is a temporal track and an invariant track,
    which are structured identically. The two tracks interact during the Analysis step in the generation of this entity
    type's data."""

    # TODO Remove default for invariant
    def __init__(self, variables: Dict[str, "Variable"], source: Optional["Track"], name: str, invariant: bool=False):
        """Do not call directly; use Track.build()."""
        self.variables: Dict[str, "Variable"] = variables
        self.name = name
        self.source = source

    @classmethod
    def build(cls, specs: Dict, source: Optional["Track"], name: str):
        """Convert specs into a Variable hierarchy, then construct a Track instance.

        :param specs: The specifications for the variables in this track.

        :param source: The source track, if any, for this track--i.e., the track corresponding to this one in the aspect
         (stage) of the analysis process that precedes this one for the particular entity type represented.

        :param name: The name of the stage/aspect."""
        track = Track(
            {
                variable_id: build_variable(variable_data)
                for variable_id, variable_data in specs.items()
            }, source, name
        )
        for variable_id, variable in track.variables.items():
            variable.set_track(track)
            variable.set_id(variable_id)
        return track

    @property
    def roots(self) -> Iterator["Variable"]:
        """All the roots of this track's variable tree."""
        return filter(
            lambda variable: not variable.parent,
            self.variables.values()
        )

    def new_var_id(self):
        # TODO Include stage name
        return 'Target_{}'.format(len(self.variables) + 1)

    def add(self, spec: Dict, var_id: str=None) -> None:
        """Validate, create, and then insert a new variable into the track."""
        if var_id is None:
            var_id = self.new_var_id()
        if var_id in self.variables:
            # Duplicated var id
            raise ValueError
        if var_id == '':
            # Invalid var id
            raise ValueError
        variable = build_variable(spec)
        variable.set_track(self)
        variable.set_id(var_id)
        Validator.validate_name(variable, variable.name)
        Validator.validate_parent(variable, variable.parent)
        Validator.validate_sources(variable, variable.sources)
        self.variables[var_id] = variable

    def duplicate(self, source_var_id: str, new_var_id: str=None):
        """Creates a duplicate of a node, including its sources, but not including its targets."""
        if new_var_id is None:
            new_var_id = self.new_var_id()
        if new_var_id in self.variables:
            raise ValueError
        self.variables[new_var_id] = deepcopy(self.variables[source_var_id])

    def delete(self, var_id: str) -> None:
        """Attempts to delete a node. Fails if the node has children or targets"""
        if var_id not in self.variables:
            raise ValueError
        variable = self.variables[var_id]
        if any(variable.children) or variable.has_targets:
            print(variable.children)
            raise ValueError
        del self.variables[var_id]

    def move(self, var_id: str, parent_id: Optional[str], sort_order: int):
        """Attempts to change the location of a node within the tree. If parent_id is None, it moves to root."""
        self.variables[var_id].parent = parent_id or ''

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0, inside_list: int=0) \
            -> Iterator[str]:
        """Provides a list of variable IDs in this track that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        :param inside_list: If -1, include only elements outside lists; if 1, only inside lists.
        """
        for variable_id, variable in self.variables.items():
            if data_type is None or variable.data_type == data_type:
                if targets:
                    if targets == -1 and variable.targets():
                        continue
                    if targets == 1 and not variable.targets():
                        continue
                if container:
                    if container == -1 and not isinstance(variable, Primitive):
                        continue
                    if container == 1 and not isinstance(variable, Container):
                        continue
                yield variable_id

    def set_primitive_expected_value(self, var_id: str, instance_id: str, value: Any):
        """Declare that a particular value is expected for a particular variable in a particular instance hierarchy.
        This is initiated in Track, rather than in Variable, in order to maintain an index of instances to be checked."""
        pass

    def remove_primitive_expected_value(self, var_id: str, instance_id: str):
        """Declare that we no longer expect any particular value for a particular variable in a particular instance."""
        pass

    def set_children_to_test(self, var_id: str, child_ids: Iterable[str]):
        """Identify the child fields whose values should be checked when verifying expected values for lists."""
        pass

    def set_list_expected_values(self, var_id: str, instance_id: str, values: Iterable[Dict[str, Any]]):
        """Indicate the (unordered) list of observations expected for selected descendents of a particular list container
        in a particular instance hierarchy"""
        pass

    def set_named_list_expected_values(self, var_id: str, instance_id: str, values: Dict[str, Dict[str, Any]]):
        """Indicate the dictionary of observations expected for selected descendents of a particular named list in a
        particular instance hierarchy"""
        pass

    @property
    def test_cases(self) -> Iterator[str]:
        """The set of all instance hierarchy IDs for which expected values have been set for any variable."""
        pass

    def dump(self) -> Dict:
        """A Dict representation of this track."""
        representation = {}
        for variable_id, variable in sorted(self.variables.items()):
            representation[variable_id] = variable.dump()
        return representation

    def dumps(self) -> str:
        """A pretty JSON string representation of this track."""
        return json.dumps(self.dump(), indent=4)
