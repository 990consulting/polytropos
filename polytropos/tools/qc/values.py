# Atomic comparators for Polytropos variables. Note that the compare_folders method is all-or-nothing, unlike what
# occurs inside CompareFixtureToActual. This all-or-nothing method is used only when comparing folders nested inside of
# Lists and NamedLists.
from typing import List as ListType, Dict, Optional, Any
from collections.abc import Callable
from polytropos.ontology.schema import Schema
import polytropos.util.compare
from polytropos.ontology.variable import Variable
from polytropos.tools.qc import POLYTROPOS_CONFIRMED_NA, POLYTROPOS_NA
from polytropos.util.nesteddicts import path_to_str

def compare_primitives(fixture: Optional[Any], actual: Optional[Any]) -> bool:
    """Compares two primitive values. Returns true if and only if they are identical, or both null."""

    if actual in {POLYTROPOS_NA, POLYTROPOS_CONFIRMED_NA}:
        raise ValueError("Actual value contained ostensibly non-occurring sentinel %s" % actual)
    if fixture is None and actual is None:
        return True

    return polytropos.util.compare.compare(fixture, actual, allow_nested=False)

class CompareComplexVariable(Callable):
    def __init__(self, schema: Schema):
        self.schema = schema
        
    def compare_lists(self, fixture: ListType[Dict], actual: Optional[ListType[Dict]], path: ListType[str]) -> bool:
        """Compares a List data type from a fixture to the List actually observed. Returns True if and only if:

            (1) The actual List exists.
            (2) There is an equal number of elements in the fixture List and the actual List.
            (3) For the nth element in each list, each of the values in the fixture element either indicate explicit
                absence (and explicit absence is confirmed) or are identical to the value corresponding to the same key
                from the actual element.

           Notes:
            - The List is treated as an atomic object, so mismatches are all-or-nothing.
            - Does NOT require that all keys present in an element from the actual list are also present in the fixture
              list, as missing child fields in the fixture represent a lack of test coverage.
            - If the List contains a List, Folder, or NamedList, a deep (recursive) comparison will be performed.
        """
        assert fixture is not False and isinstance(fixture, list)

        # (1) The actual List exists.
        if actual is None or not isinstance(actual, list):
            return False

        # (2) There is an equal number of elements in the fixture List and the actual List.
        if len(fixture) != len(actual):
            return False

        # For the nth element of each list...
        for e, a in zip(fixture, actual):  # type: Dict, Dict
            # (3) For the nth element in each list, each of the values in the fixture element either indicate explicit
            # absence (and explicit absence is confirmed) or are identical to the value corresponding to the same key
            # from the actual element.
            for key in e.keys():
                if e[key] == POLYTROPOS_NA and key not in a:
                    continue
                if key not in a:
                    return False
                if not self(e[key], a[key], path + [key]):
                    return False

        return True

    def compare_named_lists(self, fixture: Dict[str, Dict], actual: Optional[Dict[str, Dict]],
                            path: ListType[str]) -> bool:
        """Compares within a Python dictionary that represents a Polytropos "NamedList" data type. Returns True if and
        only if:

            (1) The actual NamedList exists.
            (2) There is an equal number of elements in the fixture NamedList and the actual NamedList.
            (3) Each key in the fixture NamedList exists in the actual NamedList.
            (4) For the elements in the fixture and actual NamedLists corresponding to a given key, each of the values
                in the fixture element either indicate explicit absence (and explicit absence is confirmed) or are
                identical to the value corresponding to the same key from the actual element.

           Notes:
            - The NamedList is treated as an atomic object, so mismatches are all-or-nothing.
            - Does NOT require that all keys present in an element from the actual NamedList are also present in the
              fixture NamedList, as missing child fields in the fixture represent a lack of test coverage.
            - If the NamedList contains a List, Folder, or NamedList, a deep (recursive) comparison will be performed.
            - The behavior of compare_folders and compare_named_lists are very different, even though both are comparing
              the same kind of Python object, because Folders and NamedLists have very different meanings in Polytropos.
        """
        if fixture is False or not isinstance(fixture, dict):
            print("breakpoint")
        assert fixture is not False and isinstance(fixture, dict)

        # (1) The actual NamedList exists.
        if actual is None or not isinstance(actual, dict):
            return False

        # (2) There is an equal number of elements in the fixture NamedList and the actual NamedList.
        if len(fixture) != len(actual):
            return False

        # (3) Each key in the fixture NamedList exists in the actual NamedList.
        if fixture.keys() != actual.keys():
            return False

        # For the elements in the fixture and actual NamedLists corresponding to a given key...
        for f_key in fixture.keys():
            e: Dict = fixture[f_key]
            a: Dict = actual[f_key]

            # (4) For the elements in the fixture and actual NamedLists corresponding to a given key, each of the values
            # in the fixture element either indicate explicit absence (and explicit absence is confirmed) or are
            # identical to the value corresponding to the same key from the actual element.
            for e_key in e.keys():
                if e[e_key] == POLYTROPOS_NA and e_key not in a:
                    continue
                if e_key not in a:
                    return False
                if not self(e[e_key], a[e_key], path + [e_key]):
                    return False

        return True

    def compare_folders(self, fixture: Dict[str, Any], actual: Optional[Dict[str, Any]], path: ListType[str]) -> bool:
        """Compares within a Python dictionary that represents a Polytropos "Folder" data type. Returns True if and only
           if:

            (1) The actual Folder exists.
            (2) For every key in the fixture Folder, there is a corresponding key in the actual Folder.
            (2) Every value in the fixture Folder compares True to the value corresponding to the same key in the actual
                Folder, based on the appropriate comparator (compare_folders, compare_lists, compare_primitives,
                compare_named_lists).

           Notes:
            - This comparator is used ONLY for compare_lists and compare_named_lists, as it returns False on the first
            mismatch.
            - The behavior of compare_folders and compare_named_lists are very different, even though both are comparing
              the same kind of Python object, because Folders and NamedLists have very different meanings in Polytropos.
        """
        assert fixture is not None
        if actual is None or not isinstance(actual, dict):
            return False
        for key in fixture.keys():
            if key not in actual:
                return False
            if not self(fixture[key], actual[key], path + [key]):
                return False
        return True

    def __call__(self, fixture: Any, actual: Optional[Any], path: Optional[ListType[str]] = None):
        assert fixture is not None

        # If we have a dictionary and no path, we're starting with the root
        if isinstance(fixture, dict) and path is None:
            return self.compare_folders(fixture, actual, [])

        # Otherwise, find out what kind of variable we're looking at
        var: Variable = self.schema.lookup(tuple(path))
        if var is None:
            raise ValueError("Unrecognized variable %s" % path_to_str(path))
        data_type: str = var.data_type

        if data_type == "Folder":
            return self.compare_folders(fixture, actual, path)

        if data_type == "List":
            return self.compare_lists(fixture, actual, path)

        if data_type == "NamedList":
            return self.compare_named_lists(fixture, actual, path)

        return compare_primitives(fixture, actual)