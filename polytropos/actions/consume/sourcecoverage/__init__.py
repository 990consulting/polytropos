from typing import List, Tuple, Iterable, cast

from polytropos.actions.consume.sourcecoverage.pair import SourceTargetPair
from polytropos.actions.consume.sourcecoverage.result import SourceCoverageResult
from polytropos.actions.consume.sourcecoverage.sourcecoverage import SourceCoverage
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

def test_entity_1():
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
