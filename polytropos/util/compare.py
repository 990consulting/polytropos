from math import isclose
from typing import Dict, List, Any, Optional, cast

def compare_dict(data1: Dict, data2: Dict) -> bool:
    if data1.keys() != data2.keys():
        return False
    return all(compare(data1[key], data2[key]) for key in data1)


def compare_list(data1: List, data2: List) -> bool:
    if len(data1) != len(data2):
        return False
    return all(compare(x, y) for x, y in zip(data1, data2))


def compare_str(data1: str, data2: str) -> bool:
    return data1 == data2


def compare_int(data1: int, data2: int) -> bool:
    return data1 == data2


def compare_float(data1: float, data2: float) -> bool:
    return isclose(data1, data2)


def compare(data1: Optional[Any], data2: Optional[Any], allow_nested: bool = True) -> bool:
    """Compare two json-like nested structures using approximate matching for
    numeric values"""
    if data1 is None and data2 is None:
        return True
    if data1 is None and data2 is not None:
        return False
    if data1 is not None and data2 is None:
        return False

    data1 = cast(Any, data1)
    data2 = cast(Any, data2)

    if type(data1) == int and type(data2) == float:
        return compare_float(data1, data2)
    if type(data1) == float and type(data2) == int:
        return compare_float(data1, data2)
    if type(data1) != type(data2):
        return False
    if isinstance(data1, dict) and allow_nested:
        return compare_dict(data1, data2)
    elif isinstance(data1, list) and allow_nested:
        return compare_list(data1, data2)
    elif isinstance(data1, str):
        return compare_str(data1, data2)
    elif isinstance(data1, int):
        return compare_int(data1, data2)
    elif isinstance(data1, float):
        return compare_float(data1, data2)
    else:
        raise ValueError
