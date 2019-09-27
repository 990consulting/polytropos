import copy
from typing import Dict, List

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.actions.filter.values.has_all import HasAllSpecificValues
from polytropos.ontology.composite import Composite

def test_one_temporal(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[2]]
    assert actual == expected

def test_no_narrow(schema, composites, context):
    composite_list = list(composites)
    expected: Dict = copy.deepcopy(composite_list[2].content)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    outcome: List[Composite] = list(f_iter(composite_list))
    actual: Dict = outcome[0].content
    assert actual == expected

def test_two_temporal_match(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "aaaa",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[2]]
    assert actual == expected

def test_two_temporal_no_match(schema, composites, context):
    composite_list = list(composites)
    # Both values occur in Composite 3, but not in the same period
    criteria: Dict = {
        "t_text_in_folder": "1111",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    assert len(list(f_iter(composite_list))) == 0

def test_immutable(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected

def test_temporal_and_immutable_match(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected

def test_t_and_i_immutable_wrong(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "Not the real value",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    assert len(list(f_iter(composite_list))) == 0

def test_t_and_i_temporal_wrong(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "Not the real value"
    }
    the_filter: Filter = HasAllSpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    assert len(list(f_iter(composite_list))) == 0