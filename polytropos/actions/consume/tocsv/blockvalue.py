from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Tuple, List, Iterator, Union, Deque, Optional, Any, Dict

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable, Primitive, NamedList
import itertools

def _unpack_as_singleton(var_id: str, values: Dict) -> Iterator[List[str]]:
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
class AsBlockValue(Callable):
    schema: Schema

    def find_columns_num(self, block: Tuple) -> int:
        num = 0
        for elem in block:
            if isinstance(elem, Tuple):
                num += self.find_columns_num(elem)
            else:
                var: Variable = self.schema.get(elem)
                if isinstance(var, (Primitive, NamedList)):
                    num += 1
        return num

    def _unpack_as_list(self, block: Tuple, values: List) -> Iterator[List[Optional[Any]]]:
        if values is None:
            yield [None] * len(block)
        for i, element in enumerate(values):
            yield list(self(block, element))

    def _unpack_as_named_list(self, block: Tuple, values: Dict) -> Iterator[List[Optional[Any]]]:
        if values is None:
            yield [[None] * (self.find_columns_num(block) + 1)]
            return
        for i, (key, element) in enumerate(values.items()):
            ret = list(_cartesian([[key]] + [list(self(block, element))]))
            yield from ret

    def __call__(self, block: Tuple, values: Dict) -> Iterator[List[Optional[Any]]]:
        """Takes a block of variable IDs representing a primitive, a list, or a named list (including nested lists and
        named lists) and yields lists of column values, where the columns represent a block of a larger CSV."""
        block_values: List = [None] * len(block)
        for i, subblock in enumerate(block):
            if isinstance(subblock, str):
                if not isinstance(values, dict):
                    print("breakpoint")
                assert isinstance(values, dict)
                block_values[i] = _unpack_as_singleton(subblock, values)
            elif isinstance(subblock, tuple):
                root_id: str = subblock[0]
                root_var: Variable = self.schema.get(root_id)
                dt: str = root_var.data_type
                if dt == "List":
                    nested_values: Optional[List] = values.get(root_id)
                    if nested_values is None:
                        block_values[i] = [[None] * self.find_columns_num(subblock)]
                    else:
                        cur = []
                        for k, elem in enumerate(nested_values):
                            cur.extend(list(self(subblock[1:], elem)))
                        block_values[i] = cur
                elif dt == "NamedList":
                    nested_values: Optional[Dict] = values.get(root_id)
                    block_values[i] = self._unpack_as_named_list(subblock[1:], nested_values)
                else:
                    raise ValueError('Variable "%s" (%s) is not a List or NamedList root' % (root_id, dt))
        yield from _cartesian(block_values)