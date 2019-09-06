"""Polytropos composites are arbitrarily nested for organization, like a file system. Variable paths are subject to
change. However, the underlying variable IDs are constant and do not change, and they are only nested if there is a
one-to-many relationship.

This package is responsible for converting composites to simplified representations in which variables are identified
by their variable IDs and are only nested in cases of one-to-many relationships.
"""
from collections import OrderedDict
from dataclasses import dataclass
from typing import Tuple, Dict, List as ListType, Optional, Any, Iterable, Union, Iterator, cast

from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable, GenericList, VariableId
from polytropos.util import nesteddicts

@dataclass
class Topological:
    """Given a nested tuple of variable IDs, with nesting representing one-to-many relationships, create a topological
    representation of the requested variables."""

    composite: Composite
    period: str

    def _get_root_var(self, block: Tuple) -> GenericList:
        assert isinstance(block[0], str)
        root_var_id: VariableId = cast(VariableId, block[0])
        root_var: Variable = self.composite.schema.get(root_var_id)
        if root_var is None:
            raise "Unknown variable '%s'" % root_var_id
        assert isinstance(root_var, GenericList)
        return root_var

    def _handle_keyed_list(self, content: Dict, child_elements: Iterable[Union[str, Tuple]]) \
            -> Optional[Dict]:
        ret: OrderedDict = OrderedDict()
        for key, value in content.items():
            ret[key] = self._traverse(child_elements, value)
        return ret

    def _handle_list(self, content: ListType, child_elements: Iterable[Union[str, Tuple]]) \
            -> Iterator[Dict]:
        for list_item in content:
            yield self._traverse(child_elements, list_item)

    def _add_one_to_many(self, ret: Dict, tree: Dict, block: Tuple) -> None:
        root_var: GenericList = self._get_root_var(block)
        root_path: ListType = list(root_var.relative_path)
        try:
            subtree: Union[ListType, Dict] = nesteddicts.get(tree, root_path)
        except nesteddicts.MissingDataError:
            return

        if root_var.data_type == "List":
            subtree = cast(ListType, subtree)
            ret[root_var.var_id] = list(self._handle_list(subtree, block[1:]))
        elif root_var.data_type == "KeyedList":
            subtree = cast(Dict, subtree)
            ret[root_var.var_id] = self._handle_keyed_list(subtree, block[1:])
        else:
            raise ValueError('Unexpected data type "{}" for putative root variable {}'
                             .format(root_var.data_type, root_var.var_id))

    def _one_to_one(self, tree: Dict, var_id: VariableId) -> Optional[Any]:
        var: Variable = self.composite.schema.get(var_id)
        if var is None:
            raise ValueError('Unknown variable ID "%s"' % var_id)
        path: ListType[str] = list(var.relative_path)
        return nesteddicts.get(tree, path)

    def _traverse(self, block: Iterable, tree: Dict) -> Dict:
        ret: Dict = {}
        for element in block:  # type: Union[VariableId, Tuple]
            if isinstance(element, tuple):
                self._add_one_to_many(ret, tree, element)
            else:
                try:
                    ret[element] = self._one_to_one(tree, element)
                except nesteddicts.MissingDataError:
                    continue
        return ret

    def __call__(self, block: Tuple) -> Dict:
        if self.period not in self.composite.content:
            return {}

        return self._traverse(block, self.composite.content[self.period])
