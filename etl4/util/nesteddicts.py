from typing import Optional, Any, Iterable, Dict, List

# TODO Quimey, I ported over some logic from Harpo990 that does this. If you know a C-based library does that does it
#  faster, please use that instead.

class MissingDataError(ValueError):
    pass

class IncompleteNestingError(ValueError):
    pass

def _do_get(target: Any, nodes: List[str]) -> Optional[Any]:
    if len(nodes) == 0:
        return target

    if not isinstance(target, dict):
        raise IncompleteNestingError

    key: str = nodes[0]
    cur: Any = target.get(key)

    if cur is None:
        return None

    return _do_get(cur, nodes[1:])

def _apply_default(default: Any, accept_none: bool):
    if default is None and not accept_none:
        raise MissingDataError

    return default

def get(target: Dict, spec: List[str], default: Any=None, accept_none=False):
    """Given a nested dict, traverse the specified path and return the value."""
    if spec == "":
        return target

    result: Any = _do_get(target, spec)

    if result is None:
        return _apply_default(default, accept_none)

    return result

def _get_or_init(target: Dict, key: str) -> Dict:
    if key not in target:
        target[key] = {}

    ret: Dict = target[key]
    if not isinstance(ret, Dict):
        raise IncompleteNestingError
    return ret

def _do_put(target: Dict, spec_arr: List, value: Any):
    assert len(spec_arr) > 0

    if len(spec_arr) == 1:
        key = spec_arr[0]
        target[key] = value
        return

    key = spec_arr[0]

    _get_or_init(target, key)

    _do_put(target[key], spec_arr[1:], value)


def put(target: Dict, spec: List[str], value: Any):
    """Given a nested dict, traverse the specified path and assign the value."""
    if len(spec) == 0:
        return

    _do_put(target, spec, value)

def delete(target: Dict, spec: List[str]):
    """Deletes the final node indicated."""
    name: str = spec[-1]
    root: Dict = get(target, spec[:-1], default={})
    if name in root:
        del root[name]

def pop(*args, **kwargs) -> Optional[Any]:
    val: Any = get(*args, **kwargs)
    delete(*args)
    return val
