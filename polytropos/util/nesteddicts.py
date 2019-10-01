from typing import Optional, Any, Iterable, Dict, Sequence, Iterator

NO_DEFAULT = Ellipsis

class MissingDataError(ValueError):
    pass

class IncompleteNestingError(ValueError):
    pass

def _do_get(target: Any, nodes: Sequence) -> Optional[Any]:
    if len(nodes) == 0:
        return target

    if not isinstance(target, dict):
        raise IncompleteNestingError

    key: str = nodes[0]
    if key not in target:
        raise MissingDataError

    cur: Any = target.get(key)

    return _do_get(cur, nodes[1:])

def get(target: Dict, spec: Sequence, default: Any=NO_DEFAULT, accept_none: bool=True) -> Any:
    """Given a nested dict, traverse the specified path and return the value."""
    if spec == "":
        return target

    try:
        result: Any = _do_get(target, spec)
    except MissingDataError as e:
        if default is not NO_DEFAULT:
            return default
        raise e

    if result is None and accept_none:
        return None

    if result is None and not accept_none and default == NO_DEFAULT:
        raise MissingDataError

    if result is None and not accept_none:
        return default

    return result

def _get_or_init(target: Dict, key: str) -> Dict:
    if key not in target:
        target[key] = {}

    ret: Dict = target[key]
    if not isinstance(ret, Dict):
        raise IncompleteNestingError
    return ret

def _do_put(target: Dict, spec_arr: Sequence, value: Any) -> None:
    assert len(spec_arr) > 0

    if len(spec_arr) == 1:
        key = spec_arr[0]
        target[key] = value
        return

    key = spec_arr[0]

    _get_or_init(target, key)

    _do_put(target[key], spec_arr[1:], value)


def put(target: Dict, spec: Sequence, value: Any) -> None:
    """Given a nested dict, traverse the specified path and assign the value."""
    if len(spec) == 0:
        return

    _do_put(target, spec, value)

def delete(target: Dict, spec: Sequence) -> None:
    """Deletes the final node indicated."""
    name: str = spec[-1]
    root: Dict = get(target, spec[:-1], default={})
    if name in root:
        del root[name]

def pop(target: Dict, spec: Sequence, default: Any=NO_DEFAULT, accept_none: bool=True) -> Optional[Any]:
    val: Any = get(target, spec, default, accept_none)
    delete(target, spec)
    return val

def path_to_str(path: Iterable[str]) -> str:
    return "/" + "/".join(path)

def str_to_path(path_str: str) -> Iterator[str]:
    assert path_str.startswith("/")
    yield from path_str[1:].split("/")

class MissingValue:
    pass

MISSING_VALUE: MissingValue = MissingValue()