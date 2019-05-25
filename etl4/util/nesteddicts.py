from typing import Optional, Any, Iterable, Dict


# TODO Quimey, I have to believe that there are libraries that do this nicely and are implemented in C.  I've used glom
#  in the path, but it's pure Python and it requires string concatenation, which is more wasted work.
def get(nested_dict: Dict, path: Iterable[str]) -> Optional[Any]:
    """Given a nested dict, traverse the specified path and return the value."""
    if len(path) == 1:
        return nested_dict.get(path[0])
    return get(nested_dict.get(path[0], {}), path[1:])


def put(nested_dict: Dict, path: Iterable[str], value: Optional[Any]) -> None:
    """Given a nested dict, traverse the specified path and assign the value."""
    if len(path) == 1:
        nested_dict[path[0]] = value
        return
    if path[0] not in nested_dict:
        nested_dict[path[0]] = {}
    put(nested_dict[path[0]], path[1:], value)
