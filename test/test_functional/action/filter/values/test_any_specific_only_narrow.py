import copy
from typing import Dict, List

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.actions.filter.values.has_any import HasAnySpecificValues
from polytropos.ontology.composite import Composite

def make_c3_expected(original: List[Composite]) -> List[Composite]:
    expected: List[Composite] = [copy.copy(c) for c in original]
    del expected[0].content["period_1"]
    del expected[2].content["period_2"]
    del expected[3].content["period_1"]
    del expected[3].content["period_2"]
    return expected

def test_one_temporal(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    expected: List[Composite] = make_c3_expected(composite_list)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_two_temporal_match_same(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "aaaa",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    expected: List[Composite] = make_c3_expected(composite_list)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_two_temporal_match_different(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "in a folder",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    del expected[2].content["period_2"]
    del expected[3].content["period_1"]
    del expected[3].content["period_2"]
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_immutable(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])

    # Because the only criterion is an immutable variable, it applies to all periods; consequently, all periods are
    # retained for Composite 4.
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    del expected[0].content["period_1"]
    del expected[2].content["period_1"]
    del expected[2].content["period_2"]

    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_temporal_and_immutable(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "lorem",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))

    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    del expected[2].content["period_1"]
    del expected[2].content["period_2"]
    del expected[3].content["period_2"]
    assert actual == expected

def test_t_and_i_immutable_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "Not a real value",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    for composite in expected[:-1]:
        for period in composite.periods:
            del composite.content[period]
    del expected[-1].content["period_2"]
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_t_and_i_temporal_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "Not a real value"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria, filters=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    expected: List[Composite] = [copy.copy(c) for c in composite_list]
    for composite in expected[:-1]:
        for period in composite.periods:
            del composite.content[period]
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected
