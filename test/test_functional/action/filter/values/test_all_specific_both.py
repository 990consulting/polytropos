import copy
from typing import Dict, List

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.actions.filter.values.has_all import HasAllSpecificValues
from polytropos.ontology.composite import Composite

def test_one_temporal(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List[Composite] = [copy.copy(composite_list[2])]
    del expected[0].content["period_2"]
    assert actual == expected

def test_two_temporal_match(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "aaaa",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [copy.copy(composite_list[2])]
    del expected[0].content["period_2"]
    assert actual == expected

def test_two_temporal_no_match(schema, composites):
    composite_list = list(composites)
    # Both values occur in Composite 3, but not in the same period
    criteria: Dict = {
        "t_text_in_folder": "1111",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    assert len(list(f_iter(composite_list))) == 0

def test_immutable(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected

def test_temporal_and_immutable_match(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List[Composite] = [copy.copy(composite_list[3])]
    del expected[0].content["period_2"]
    assert actual == expected

def test_t_and_i_immutable_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "Not the real value",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    assert len(list(f_iter(composite_list))) == 0

def test_t_and_i_temporal_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "Not the real value"
    }
    the_filter: Filter = HasAllSpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    assert len(list(f_iter(composite_list))) == 0
