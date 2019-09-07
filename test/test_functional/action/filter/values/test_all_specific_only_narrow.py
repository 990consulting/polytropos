import copy
from typing import Dict, List

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.actions.filter.values.has_all import HasAllSpecificValues
from polytropos.ontology.composite import Composite

def make_c3_expected(original: List[Composite]) -> List[Composite]:
    expected: List[Composite] = [copy.copy(c) for c in original]
    del expected[0].content["period_1"]
    del expected[2].content["period_2"]
    del expected[3].content["period_1"]
    del expected[3].content["period_2"]
    return expected

def purge_all_periods(original: List[Composite]) -> List[Composite]:
    expected: List[Composite] = [copy.copy(c) for c in original]
    for composite in expected:
        for period in composite.periods:
            del composite.content[period]
    return expected

def test_one_temporal(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    expected: List[Composite] = make_c3_expected(composite_list)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_two_temporal_match(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "aaaa",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    expected: List[Composite] = make_c3_expected(composite_list)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_two_temporal_no_match(schema, composites):
    composite_list = list(composites)

    criteria: Dict = {
        "t_text_in_folder": "cccc",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])

    # Because the criteria contain no immutable variables, only temporal periods are purged
    expected: List[Composite] = purge_all_periods(composite_list)

    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_immutable(schema, composites):
    composite_list = list(composites)
    expected: List[Composite] = [copy.copy(c) for c in composite_list]

    # Because the criteria contain immutable variables, everything is purged
    for composite in expected[:-1]:
        composite.content = {}

    criteria: Dict = {
        "i_text_in_folder": "I(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_temporal_and_immutable_match(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "P1(folder)"
    }

    # Because the criteria contain immutable variables, everything is purged for composites 1-3. For composite 4, the
    # non-matching period is also purged.
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    for composite in expected[:-1]:
        composite.content = {}
    del expected[3].content["period_2"]

    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_t_and_i_immutable_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "Not the real value",
        "t_text_in_folder": "P1(folder)"
    }

    # Because the immutable value is wrong in Composite 4, every period is purged in every composite
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    for composite in expected:
        composite.content = {}

    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_t_and_i_temporal_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "Not the real value"
    }

    # Because the immutable value is right in Composite 4, the immutable values remain in that composite; everything
    # else is purged from all of the composites
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    for composite in expected[:-1]:
        composite.content = {}
    for period in expected[-1].periods:
        del expected[-1].content[period]

    the_filter: Filter = HasAllSpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected
