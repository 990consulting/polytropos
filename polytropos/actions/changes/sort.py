from collections import OrderedDict
from typing import Dict, List, Set, Optional, Any, cast

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable

class Sort(Change):
    """Sorts variables at every level of the hierarchy according to their sort order. Variables not in the schema are
    included at the beginning of the sort order. Lists, KeyedLists, and MultipleText fields are not sorted
    internally."""

    def _get_sorted_keys(self, to_sort: Dict, path: List[str]) -> Dict[str, Optional[Variable]]:
        in_schema: Dict[str, Variable] = {}
        not_in_schema: Set[str] = set()
        for key in to_sort.keys():
            key_path: List[str] = path + [key]
            var: Optional[Variable] = self.schema.lookup(key_path)
            if var is None:
                not_in_schema.add(key)
                continue
            in_schema[key] = var

        ret: OrderedDict = OrderedDict()
        for key in sorted(not_in_schema):
            ret[key] = None
        for key in sorted(in_schema.keys(), key=lambda k: in_schema[k].sort_order):
            ret[key] = in_schema[key]

        return ret

    def _sort_within_list_items(self, to_sort: List[Dict], path: List[str]) -> List[Dict]:
        """Sort the data inside of list elements. DO NOT sort the list items themselves."""

        ret: List[Optional[Dict]] = [None] * len(to_sort)
        for i, child in enumerate(to_sort):
            ret[i] = self._sort_within_folder(child, path)

        return cast(List[Dict], ret)

    def _sort_within_keyed_list_items(self, to_sort: Dict, path: List[str]) -> Dict:
        ret: Dict = OrderedDict()
        for key, value in to_sort.items():
            ret[key] = self._sort_within_folder(value, path)

        return ret

    def _sort_within_folder(self, to_sort: Optional[Dict], path: List[str]) -> Optional[Dict]:
        if to_sort is None:
            return None
        sorted_keys: Dict[str, Optional[Variable]] = self._get_sorted_keys(to_sort, path)
        ret: OrderedDict = OrderedDict()
        for key, var in sorted_keys.items():
            value: Optional[Any] = to_sort[key]
            key_path: List[str] = path + [key]
            if var is None or value is None:
                ret[key] = value
            elif var.data_type == "List":
                ret[key] = self._sort_within_list_items(value, key_path)
            elif var.data_type == "KeyedList":
                ret[key] = self._sort_within_keyed_list_items(value, key_path)
            elif var.data_type == "Folder":
                ret[key] = self._sort_within_folder(value, key_path)
            else:
                ret[key] = value
        return ret

    def __call__(self, composite: Composite) -> None:
        content: OrderedDict = OrderedDict()
        periods: List[str] = sorted(composite.periods)
        for period in periods:
            to_sort: Dict = composite.content[period]
            content[period] = self._sort_within_folder(to_sort, [])

        if "immutable" in composite.content:
            content["immutable"] = self._sort_within_folder(composite.content["immutable"], [])

        composite.content = content