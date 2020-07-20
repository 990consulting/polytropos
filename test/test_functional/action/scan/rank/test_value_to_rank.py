from collections import Counter
from typing import Dict, Any

from polytropos.actions.scan.rank import value_to_rank

def test_one_observation():
    c: Counter = Counter()
    c[5/3] = 1
    expected: Dict[Any, int] = {5/3: 1}
    actual: Dict[Any, int] = value_to_rank(c)
    assert actual == expected

def test_all_same_value():
    c: Counter = Counter()
    c[5/3] = 10
    expected: Dict[Any, int] = {5/3: 10}
    actual: Dict[Any, int] = value_to_rank(c)
    assert actual == expected

def test_two_values():
    c: Counter = Counter()
    c[5/3] = 2
    c[2] = 8
    expected: Dict[Any, int] = {
        2: 8,
        5/3: 10
    }
    actual: Dict[Any, int] = value_to_rank(c)
    assert actual == expected

def test_one_of_each_value():
    c: Counter = Counter()
    for i in range(1, 11):
        c[i / 10.0] = 1
    expected: Dict[Any, int] = {i / 10: 11 - i for i in range(1, 11)}
    actual: Dict[Any, int] = value_to_rank(c)
    assert actual == expected

def test_outliers():
    c: Counter = Counter()
    c[1] = 1
    c[2] = 8
    c[1000000] = 1
    expected: Dict[Any, int] = {
        1000000: 1,
        2: 9,
        1: 10
    }
    actual: Dict[Any, int] = value_to_rank(c)
    assert actual == expected

def test_negative_values():
    c: Counter = Counter()
    c[-1] = 1
    c[0] = 2
    c[1] = 1
    expected: Dict[Any, int] = {
        1: 1,
        0: 3,
        -1: 4
    }
    actual: Dict[Any, int] = value_to_rank(c)
    assert actual == expected
