import json
from typing import Iterator, Dict, TYPE_CHECKING, List, Any, Iterable
from etl4.ontology.variable import build_variable

if TYPE_CHECKING:
    from etl4.ontology.variable import Variable

class Track:

    def __init__(self, variables: Dict, name: str):
        self.variables = variables
        self.name = name

    @classmethod
    def build(cls, specs: Dict, name: str):
        """Convert specs into a Variable hierarchy, then construct a Track instance."""
        return Track(
            {
                variable_id: build_variable(variable_data)
                for variable_id, variable_data in specs.items()
            }, name
        )

    def roots(self) -> Iterator["Variable"]:
        """Gets an iterator of all the roots of this track's variable tree."""
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

    def move(self, var_id: str, parent_id: str, sort_order: int):
        """Attempts to change the location of a node within the tree."""
        pass

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0) -> Iterator[str]:
        """Provides a list of variable IDs in this track that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        """
        pass

    @property
    def as_list(self) -> List:
        """A list representation of this variable."""
        pass

    @property
    def json(self) -> str:
        """A JSON-compatible list representation of this track. (For serialization.)"""
        return json.dumps(self.as_list)

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

    def set_list_expected_values(self, var_id: str, instance_id: str, values: Iterable[str, Any]):
        """Indicate the (unordered) list of observations expected for selected descendents of a particular list container
        in a particular instance hierarchy"""
        pass

    def set_named_list_expected_values(self, var_id: str, instance_id: str, values: Dict[str, Any]):
        """Indicate the dictionary of observations expected for selected descendents of a particular named list in a
        particular instance hierarchy"""
        pass

    @property
    def test_cases(self) -> Iterator[str]:
        """The set of all instance hierarchy IDs for which expected values have been set for any variable."""
        pass

