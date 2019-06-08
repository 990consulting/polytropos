from copy import deepcopy
import json
from typing import Iterator, Dict, TYPE_CHECKING, Any, Iterable, Optional
from polytropos.ontology.variable import (
    build_variable,
    Primitive, Container, GenericList, Validator,
    List, NamedList
)

if TYPE_CHECKING:
    from polytropos.ontology.variable import Variable

class Track:
    """Represents a hierarchy of variables associated with a particular aspect (stage) of a particular entity type, and
    that have the same temporality. That is, for every entity type, there is a temporal track and an immutable track,
    which are structured identically. The two tracks interact during the Analysis step in the generation of this entity
    type's data."""

    def __init__(self, variables: Dict[str, "Variable"], source: Optional["Track"], name: str):
        """Do not call directly; use Track.build()."""
        self.variables: Dict[str, "Variable"] = variables
        self.name = name
        self.source = source
        self.target = None
        if source:
            source.target = self


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
        # we only validate after the whole thing is built to be able to
        # accurately compute siblings, parents and children
        for variable in track.variables.values():
            Validator.validate(variable, init=True)
        return track

    @property
    def roots(self) -> Iterator["Variable"]:
        """All the roots of this track's variable tree."""
        return filter(
            lambda variable: variable.parent == '',
            self.variables.values()
        )

    def new_var_id(self):
        """If no ID is supplied, use <stage name>_<temporal|invarant>_<n+1>,
        where n is the number of variables."""
        # Missing the temporal/immutable part for now
        return '{}_{}'.format(self.name, len(self.variables) + 1)

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
        Validator.validate(variable, init=True, adding=True)
        variable.update_sort_order(None, variable.sort_order)
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
        variable.update_sort_order(variable.sort_order, None)
        if any(variable.children) or variable.has_targets:
            raise ValueError
        del self.variables[var_id]

    def move(self, var_id: str, parent_id: Optional[str], sort_order: int):
        """Attempts to change the location of a node within the tree. If parent_id is None, it moves to root."""
        variable = self.variables[var_id]
        parent_id = parent_id or ''
        if parent_id and parent_id not in self.variables:
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

    def set_primitive_expected_value(self, var_id: str, instance_id: str, value: Any):
        """Declare that a particular value is expected for a particular variable in a particular instance hierarchy.
        This is initiated in Track, rather than in Variable, in order to maintain an index of instances to be checked."""
        self.variables[var_id].simple_expected_values[instance_id] = value

    def remove_primitive_expected_value(self, var_id: str, instance_id: str):
        """Declare that we no longer expect any particular value for a particular variable in a particular instance."""
        variable = self.variables[var_id]
        if isinstance(variable, Primitive):
            del variable.simple_expected_values[instance_id]
        if isinstance(variable, List):
            del variable.list_expected_values[instance_id]
        if isinstance(variable, NamedList):
            del variable.named_list_expected_values[instance_id]

    def set_children_to_test(self, var_id: str, child_ids: Iterable[str]):
        """Identify the child fields whose values should be checked when verifying expected values for lists."""
        variable = self.variables[var_id]
        variable.list_expected_values_fields = []
        evs = (
            variable.list_expected_values
            if isinstance(variable, List)
            else variable.named_list_expected_values
        )
        for child_id in child_ids:
            if child_id not in self.variables:
                raise ValueError
            variable.list_expected_values_fields.append(child_id)
            for _lst in evs.values():
                lst = _lst if isinstance(variable, List) else _lst.values()
                for value in lst:
                    if child_id not in value:
                        value[child_id] = None
        for _lst in evs.values():
            lst = _lst if isinstance(variable, List) else _lst.values()
            for value in lst:
                for key in list(value.keys()):
                    if key not in variable.list_expected_values_fields:
                        del value[key]


    def set_list_expected_values(self, var_id: str, instance_id: str, values: Iterable[Dict[str, Any]]):
        """Indicate the (unordered) list of observations expected for selected descendents of a particular list container
        in a particular instance hierarchy"""
        variable = self.variables[var_id]
        variable.list_expected_values[instance_id] = []
        for value in values:
            if list(value.keys()) != variable.list_expected_values_fields:
                print(value.keys(), variable.list_expected_values_fields)
                raise ValueError
            variable.list_expected_values[instance_id].append(value)


    def set_named_list_expected_values(self, var_id: str, instance_id: str, values: Dict[str, Dict[str, Any]]):
        """Indicate the dictionary of observations expected for selected descendents of a particular named list in a
        particular instance hierarchy"""
        variable = self.variables[var_id]
        variable.named_list_expected_values[instance_id] = {}
        for key, value in values.items():
            if list(value.keys()) != variable.list_expected_values_fields:
                print(value.keys(), variable.list_expected_values_fields)
                raise ValueError
            variable.named_list_expected_values[instance_id][key] = value

    @property
    def test_cases(self) -> Iterator[str]:
        """The set of all instance hierarchy IDs for which expected values have been set for any variable."""
        for variable in self.variables.values():
            for test_case in variable.test_cases:
                yield test_case

    def dump(self) -> Dict:
        """A Dict representation of this track."""
        representation = {}
        for variable_id, variable in sorted(self.variables.items()):
            representation[variable_id] = variable.dump()
        return representation

    def dumps(self) -> str:
        """A pretty JSON string representation of this track."""
        return json.dumps(self.dump(), indent=4)
