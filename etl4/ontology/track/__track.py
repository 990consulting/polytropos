from typing import Iterable, Dict

from etl4.ontology.variable import build_variable


class Track:

    def __init__(self, variables):
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
