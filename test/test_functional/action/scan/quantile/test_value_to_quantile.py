from collections import Counter
from typing import Dict

from polytropos.actions.scan.quantile import val2qtile

def test_one_observation():
    c: Counter = Counter()
    c[1] = 1
    expected: Dict[int, float] = {1: 0.0}
    actual: Dict[int, float] = val2qtile(c)
    assert actual == expected

def test_all_same_value():
    c: Counter = Counter()
    c[1] = 10
    expected: Dict[int, float] = {1: 0.0}
    actual: Dict[int, float] = val2qtile(c)
    assert actual == expected

def test_two_values():
    c: Counter = Counter()
    c[1] = 2
    c[2] = 8
    expected: Dict[int, float] = {
        1: 0.0,
        2: 0.2
    }
    actual: Dict[int, float] = val2qtile(c)
    assert actual == expected

def test_one_of_each_value():
    c: Counter = Counter()
    for i in range(1, 11):
        c[i] = 1
    expected: Dict[int, float] = {i + 1: i / 10 for i in range(10)}
    actual: Dict[int, float] = val2qtile(c)
    assert actual == expected

def test_outliers():
    c: Counter = Counter()
    c[1] = 1
    c[2] = 8
    c[1000000] = 1
    expected: Dict[int, float] = {
        1: 0.0,
        2: 0.1,
        1000000: 0.9
    }
    actual: Dict[int, float] = val2qtile(c)
    assert actual == expected

def test_negative_values():
    c: Counter = Counter()
    c[-1] = 1
    c[0] = 2
    c[1] = 1
    expected: Dict[int, float] = {
        -1: 0.0,
        0: .25,
        1: 0.75
    }
    actual: Dict[int, float] = val2qtile(c)
    assert actual == expected
