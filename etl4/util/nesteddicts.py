from typing import Optional, Any, Iterable, Dict

# TODO Quimey, I have to believe that there are libraries that do this nicely and are implemented in C.  I've used glom
#  in the path, but it's pure Python and it requires string concatenation, which is more wasted work.

def get(nested_dict: Dict, path: Iterable[str]) -> Optional[Any]:
    """Given a nested dict, traverse the specified path and return the value."""
    pass

def put(nested_dict: Dict, path: Iterable[str], value: Optional[Any]) -> None:
    """Given a nested dict, traverse the specified path and assign the value."""
    pass