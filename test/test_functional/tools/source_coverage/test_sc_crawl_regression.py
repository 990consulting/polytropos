"""Isolating unexpected results in crawl of entity_1.json from Lifecycle."""
import json
import os
from typing import Dict, List, Tuple

import pytest

@pytest.fixture()
def e1_trans(basepath: str) -> Dict:
    fixture_path: str = os.path.join(basepath, "test_functional", "tools", "source_coverage", "fixtures",
                                     "text_no_trivial")

    translate_fn: str = os.path.join(fixture_path, "translate", "ent", "ity", "entity_1.json")
    with open(translate_fn) as translate_fh:
        translation: Dict = json.load(translate_fh)
    return translation

@pytest.fixture()
def e1_trace(basepath: str) -> Dict:
    fixture_path: str = os.path.join(basepath, "test_functional", "tools", "source_coverage", "fixtures",
                                     "text_no_trivial")

    trace_fn: str = os.path.join(fixture_path, "trace", "ent", "ity", "entity_1.json")
    with open(trace_fn) as trace_fh:
        trace: Dict = json.load(trace_fh)
    return trace

def test_immutable_only(do_crawl_test, e1_trace, e1_trans):
    translation: Dict = {"immutable": e1_trans["immutable"]}
    trace: Dict = {"immutable": e1_trace["immutable"]}

    expected_pair_counts: List[Tuple[str, str, int]] = [
        ("source_i_keyed_list_text_1_1", "target_i_keyed_list_text_1", 2),
        ("source_i_folder_text_2_2", "target_i_folder_text_2", 1)
    ]
    do_crawl_test(translation, trace, expected_pair_counts)

def test_201210_only(do_crawl_test, e1_trace, e1_trans):
    translation: Dict = {"201210": e1_trans["201210"]}
    trace: Dict = {"201210": e1_trace["201210"]}

    expected_pair_counts: List[Tuple[str, str, int]] = [
        ("source_t_folder_text_1_1", "target_t_folder_text_1", 1),
        ("source_t_list_text_1_1", "target_t_list_text_1", 1),
        ("source_t_list_text_1_2", "target_t_list_text_2", 1),
        ("source_t_keyed_list_text_1_1", "target_t_keyed_list_text_1", 2),
        ("source_t_keyed_list_text_1_2", "target_t_keyed_list_text_2", 2)
    ]
    do_crawl_test(translation, trace, expected_pair_counts)

def test_201310_only(do_crawl_test, e1_trace, e1_trans):
    translation: Dict = {"201310": e1_trans["201310"]}
    trace: Dict = {"201310": e1_trace["201310"]}

    expected_pair_counts: List[Tuple[str, str, int]] = [
        ("source_t_folder_text_1_2", "target_t_folder_text_2", 1)
    ]
    do_crawl_test(translation, trace, expected_pair_counts)

def test_201410_only(do_crawl_test, e1_trace, e1_trans):
    """In the 2014 case, the target list is nested incorrectly, resulting in a variable that is not defined in the
    schema. Values that do not conform to known variable paths in the schema are not included. As a result, we only
    expect reported coverage for /target_t_folder/target_text_1 (target_t_folder_text_1)."""

    translation: Dict = {"201410": e1_trans["201410"]}
    trace: Dict = {"201410": e1_trace["201410"]}

    expected_pair_counts: List[Tuple[str, str, int]] = [
        ("source_t_folder_text_1_1", "target_t_folder_text_1", 1)
    ]
    do_crawl_test(translation, trace, expected_pair_counts)

def test_entity1_all(do_crawl_test, e1_trace, e1_trans):
    expected_pair_counts: List[Tuple[str, str, int]] = [
        ("source_t_folder_text_1_1", "target_t_folder_text_1", 2),
        ("source_t_folder_text_1_2", "target_t_folder_text_2", 1),
        ("source_t_list_text_1_1", "target_t_list_text_1", 1),
        ("source_t_list_text_1_2", "target_t_list_text_2", 1),
        ("source_t_keyed_list_text_1_1", "target_t_keyed_list_text_1", 2),
        ("source_t_keyed_list_text_1_2", "target_t_keyed_list_text_2", 2),
        ("source_i_keyed_list_text_1_1", "target_i_keyed_list_text_1", 2),
        ("source_i_folder_text_2_2", "target_i_folder_text_2", 1)
    ]
    do_crawl_test(e1_trans, e1_trace, expected_pair_counts)
