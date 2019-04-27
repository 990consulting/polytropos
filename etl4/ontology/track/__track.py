from typing import Iterator, Dict, TYPE_CHECKING
from etl4.ontology.variable import build_variable

if TYPE_CHECKING:
    from etl4.ontology.variable import Variable

class Track:

    def __init__(self, variables: Dict):
        self.variables = variables

    @classmethod
    def build(cls, specs: Dict):
        """Convert specs into a Variable hierarchy, then construct a Track instance."""
        return Track(
            {
                variable_id: build_variable(variable_data)
                for variable_id, variable_data in specs.items()
            }
        )

    def roots(self) -> Iterator["Variable"]:
        """Gets an iterator of all the roots of this track's variable tree."""
        pass

    def insert(self, spec: Dict, var_id: str=None) -> None:
        """Validate and then insert a new variable into the track."""
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
