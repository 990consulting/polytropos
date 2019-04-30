import json
from typing import Iterator, Dict, TYPE_CHECKING, List, Any, Iterable, Optional
from etl4.ontology.variable import build_variable

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

        return Track(
            {
                variable_id: build_variable(variable_data)
                for variable_id, variable_data in specs.items()
            }, source, name
        )

    @property
    def roots(self) -> Iterator["Variable"]:
        """All the roots of this track's variable tree."""
        pass

    def add(self, spec: Dict, var_id: str=None) -> None:
        """Validate, create, and then insert a new variable into the track."""
        pass

    def duplicate(self, source_var_id: str, new_var_id: str=None):
        """Creates a duplicate of a node, including its sources, but not including its targets."""
        pass

    def delete(self, var_id: str) -> None:
        """Attempts to delete a node. Fails if the node has children or targets"""
        pass

    def move(self, var_id: str, parent_id: Optional[str], sort_order: int):
        """Attempts to change the location of a node within the tree. If parent_id is None, it moves to root."""
        pass

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0) -> Iterator[str]:
        """Provides a list of variable IDs in this track that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        """
        pass

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
        pass

    def dumps(self) -> str:
        """A pretty JSON string representation of this track."""
        pass
