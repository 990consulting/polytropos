import os
from typing import List, Tuple, Iterable, cast, Dict, Callable
import json

from polytropos.actions.consume.sourcecoverage.crawl import Crawl
from polytropos.actions.consume.sourcecoverage.pair import SourceTargetPair
from polytropos.actions.consume.sourcecoverage.result import SourceCoverageResult
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import VariableId

def _as_result(counts: Iterable[Tuple[str, str, int]]) -> SourceCoverageResult:
    ret: SourceCoverageResult = SourceCoverageResult()
    for source_var_str, target_var_str, n_obs in counts:
        source_var: VariableId = cast(VariableId, source_var_str)
        target_var: VariableId = cast(VariableId, target_var_str)
        pair: SourceTargetPair = SourceTargetPair(source_var, target_var)
        ret.observed_pairs.add(pair)
        ret.pair_counts[pair] = n_obs
    return ret

def test_entity_1(basepath: str, source_schema: Callable, target_schema: Callable):
    fixture_path: str = os.path.join(basepath, "test_functional", "tools", "source_coverage", "fixtures",
                                     "text_no_trivial")

    trace_fn: str = os.path.join(fixture_path, "trace", "ent", "ity", "entity_1.json")
    translate_fn: str = os.path.join(fixture_path, "translate", "ent", "ity", "entity_1.json")

    with open(trace_fn) as trace_fh, open(translate_fn) as translate_fh:
        trace: Dict = json.load(trace_fh)
        translation: Dict = json.load(translate_fh)

    source: Schema = source_schema("Text")
    target: Schema = target_schema(source, "Text")

    crawl: Crawl = Crawl("entity_1", target)

    expected_pair_counts: List[Tuple[str, str, int]] = [
        ("source_t_folder_text_1_1", "target_t_folder_text_1", 2),
        ("source_t_list_text_1_2", "target_t_list_text_2", 2),
        ("source_t_keyed_list_text_1_2", "target_t_keyed_list_text_2", 2),
        ("source_t_keyed_list_text_1_1", "target_t_keyed_list_text_1", 2),
        ("source_t_folder_text_1_2", "target_t_folder_text_2", 1),
        ("source_t_list_text_1_1", "target_t_list_text_1", 1),
        ("source_i_keyed_list_text_1_1", "target_i_keyed_list_text_1", 2),
        ("source_i_folder_text_2_2", "target_i_folder_text_2", 1)
    ]
    expected: SourceCoverageResult = _as_result(expected_pair_counts)
    actual: SourceCoverageResult = crawl(translation, trace)
    assert actual == expected