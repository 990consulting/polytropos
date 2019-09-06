from collections import deque
from dataclasses import dataclass
from typing import Tuple, List, Iterator, Union, Deque, Optional, Any, Dict, cast

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable, Primitive, KeyedList, VariableId
import itertools

def _unpack_as_singleton(var_id: str, values: Dict) -> Iterator[List]:
    value: Optional[Any] = values.get(var_id)
    yield [[value]]

# SO 10823877
def flatten(container: Union[List, Tuple]) -> Iterator:
    """Flattens an arbitrarily nested list."""
    for i in container:
        if isinstance(i, (list, tuple)):  # I didn't know you could supply a tuple of classes...
            for j in flatten(i):
                yield j
        else:
            yield i

def _cartesian(block_values: List) -> Iterator[List[Optional[Any]]]:
    """Starts with an arbitrarily nested list of lists, where each singly nested list represents all observed values for
    one or more columns in a spreadsheet column block. Yields lists representing rows of the column block."""
    for nested in itertools.product(*block_values):
        yield list(flatten(nested))

@dataclass
class AsBlockValue:
    schema: Schema

    def find_num_columns(self, block: Tuple) -> int:
        num_columns: int = 0
        for subblock in block:
            if isinstance(subblock, tuple):
                num_columns += self.find_num_columns(subblock)
            else:
                var: Variable = self.schema.get(subblock)
                if isinstance(var, (Primitive, KeyedList)):
                    num_columns += 1
        return num_columns

    def _unpack_as_list(self, block: Tuple, values: Optional[List]) -> Iterator[List[Optional[Any]]]:
        if values is None:
            yield [[None] * self.find_num_columns(block)]
        else:
            for element in values:
                yield from self(block, element)

    def _unpack_as_keyed_list(self, block: Tuple, values: Optional[Dict]) -> Iterator[List[Optional[Any]]]:
        if values is None:
            yield [[None] * (self.find_num_columns(block) + 1)]
            return
        for key, element in values.items():
            yield from _cartesian([[key]] + [list(self(block, element))])

    def __call__(self, block: Tuple, values: Dict) -> Iterator[List[Optional[Any]]]:
        """Takes a block of variable IDs representing a primitive, a list, or a keyed list (including nested lists and
        keyed lists) and yields lists of column values, where the columns represent a block of a larger CSV."""
        block_values: List = [None] * len(block)
        for i, subblock in enumerate(block):
            if isinstance(subblock, str):
                block_values[i] = _unpack_as_singleton(subblock, values)
            elif isinstance(subblock, tuple):
                root_id: VariableId = subblock[0]
                root_var: Variable = self.schema.get(root_id)
                dt: str = root_var.data_type
                if dt == "List":
                    list_items: Optional[List] = values.get(root_id)
                    block_values[i] = self._unpack_as_list(subblock[1:], list_items)
                elif dt == "KeyedList":
                    keyed_list_items: Optional[Dict] = values.get(root_id)
                    block_values[i] = self._unpack_as_keyed_list(subblock[1:], keyed_list_items)
                else:
                    raise ValueError('Variable "%s" (%s) is not a List or KeyedList root' % (root_id, dt))
        yield from _cartesian(block_values)