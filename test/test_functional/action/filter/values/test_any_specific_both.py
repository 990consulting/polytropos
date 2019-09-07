import copy
from typing import Dict, List

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.actions.filter.values.has_any import HasAnySpecificValues
from polytropos.ontology.composite import Composite

def test_one_temporal(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List[Composite] = [composite_list[2]]
    del expected[0].content["period_2"]
    assert actual == expected

def test_two_temporal_match_same(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "aaaa",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[2]]
    del expected[0].content["period_2"]
    assert actual == expected

def test_two_temporal_match_different(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "in a folder",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    expected: List = [composite_list[0], composite_list[2]]
    del expected[1].content["period_2"]
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_immutable(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected

def test_temporal_and_immutable_match(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "lorem",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List[Composite] = [composite_list[0], composite_list[3]]
    del expected[1].content["period_2"]
    assert actual == expected

def test_t_and_i_immutable_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "Not a real value",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    del expected[0].content["period_2"]
    assert actual == expected

def test_t_and_i_temporal_wrong(schema, composites):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "Not a real value"
    }
    the_filter: Filter = HasAnySpecificValues(schema, criteria)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected
