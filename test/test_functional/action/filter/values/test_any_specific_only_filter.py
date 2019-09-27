import copy
from typing import Dict, List

from polytropos.actions.filter import Filter
from polytropos.actions.filter.mem import InMemoryFilterIterator
from polytropos.actions.filter.values.has_any import HasAnySpecificValues
from polytropos.ontology.composite import Composite

def test_one_temporal(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[2]]
    assert actual == expected

def test_no_narrow(schema, composites, context):
    composite_list = list(composites)
    expected: Dict = copy.deepcopy(composite_list[2].content)
    criteria: Dict = {"t_text_in_root": "bbbb"}
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    outcome: List[Composite] = list(f_iter(composite_list))
    actual: Dict = outcome[0].content
    assert actual == expected

def test_two_temporal_match_same(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "aaaa",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[2]]
    assert actual == expected

def test_two_temporal_match_different(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "t_text_in_folder": "in a folder",
        "t_text_in_root": "bbbb"
    }
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    expected: List = [composite_list[0], composite_list[2]]
    actual: List[Composite] = list(f_iter(composite_list))
    assert actual == expected

def test_immutable(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected

def test_temporal_and_immutable_match(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "lorem",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[0], composite_list[3]]
    assert actual == expected

def test_t_and_i_immutable_wrong(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "Not a real value",
        "t_text_in_folder": "P1(folder)"
    }
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected

def test_t_and_i_temporal_wrong(schema, composites, context):
    composite_list = list(composites)
    criteria: Dict = {
        "i_text_in_folder": "I(folder)",
        "t_text_in_folder": "Not a real value"
    }
    the_filter: Filter = HasAnySpecificValues(context, schema, criteria, narrows=False)
    f_iter: InMemoryFilterIterator = InMemoryFilterIterator([the_filter])
    actual: List[Composite] = list(f_iter(composite_list))
    expected: List = [composite_list[3]]
    assert actual == expected
