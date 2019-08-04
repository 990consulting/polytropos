from collections.abc import Callable
from dataclasses import dataclass
from typing import List, Iterator, Tuple

from polytropos.actions.consume.tocsv.valueset import ValueSet
from polytropos.ontology.schema import Schema

def cartesian(block_values) -> Iterator[List]:
    """A block consists of a list of columns, which may be just one column. This generator yields lists that represent
    rows of the CSV.

    The innermost list of block_values is the """
    pass

@dataclass
class AsRows(Callable):
    schema: Schema

    # Each list item is a tuple of variable IDs. If the tuple is of length greater than one, the first must be the
    # variable ID of a list or named list, and the subsequent values are descendants of that list. Tuples may be
    # nested in case of nested lists or named lists.
    column_order: List[Tuple]

    def _get_block_value(self, block: Tuple, temporal_values: ValueSet, immutable_values: ValueSet) -> List[List[str]]:
        pass

    def __call__(self, values: ValueSet) -> Iterator[List]:
        block_values: List[List[List]] = [None] * len(self.column_order)
        for i, block in enumerate(self.column_order):
            block_value_list: List[List] = self._get_block_value(block, temporal_values, immutable_values)
            block_values[i] = block_value_list
        yield from cartesian(block_values)
