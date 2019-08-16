from collections.abc import Callable
from dataclasses import dataclass
from typing import List, Tuple

from polytropos.ontology.schema import Schema

class DescriptorsToBlocks(Callable):
    """Convert a list of column descriptors to column blocks, which can in turn be used to extract data."""
    def __call__(self, descriptors: List) -> Tuple:
        pass

@dataclass
class DescriptorsToColumnNames(Callable):
    """Convert a list of column descriptors to column names. By default, the column names are the absolute path of the
    variables, but these column names can be overridden."""

    schema: Schema

    def __call__(self, descriptors: List) -> Tuple:
        """NOTE FOR FREELANCER:

        The YAML supplied in the tests contains variable IDs (eg., "i_outer_nested_named_list.") To convert this into
        the "absolute path" required for the task, call

            self.schema.get(var_id).absolute_path

        where "var_id" is the variable ID whose path you want."""
        pass
