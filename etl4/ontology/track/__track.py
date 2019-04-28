import json
from typing import Iterator, Dict, TYPE_CHECKING, List
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
