import pickle
from collections import defaultdict, Mapping
from typing import Dict, Set, Tuple, List, Optional, Iterator

from polytropos.actions.consume.source_coverage._var_info import VarInfo
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import VariableId, Variable

def _import_var_pairs(schema: Optional[Schema]) -> Set[VarInfo]:
    ret: Set[VarInfo] = set()

    for target_var in schema:  # type: Variable
        target_var_id: VariableId = target_var.var_id
        for source_var_id in target_var.sources:
            var_info: VarInfo = VarInfo(source_var_id, target_var_id)
            ret.add(var_info)
    return ret

class SourceCoverageResult:
    """Represents observed source->value pairs in a scan of the actual data."""

    def __init__(self) -> None:
        self._observed_vars: Set[VarInfo] = set()
        self._var_counts: Dict[VarInfo, int] = defaultdict(int)

    def update(self, all_vars: Set[VarInfo], observed_paths: Dict[VarInfo, Set[Tuple[str, ...]]]) -> None:
        """Update the result with new data from given ein/period."""

        for var_info, target_paths in observed_paths.items():
            assert len(target_paths) == 1
            self._var_counts[var_info] += 1
        self._observed_vars.update(all_vars)

    def serialize_state(self, state_path: str) -> None:
        """Return serialized state to send it to the master process."""

        all_vars: List[VarInfo] = list(self._observed_vars)
        all_vars_indexes: Dict[VarInfo, int] = {var_info: i for i, var_info in enumerate(all_vars)}
        var_counts: Dict[int, int] = {all_vars_indexes[var_info]: count for var_info, count in self._var_counts.items()}
        with open(state_path, "wb") as f:
            pickle.dump((all_vars, var_counts), f)

class MergedSourceCoverageResult(Mapping):
    """Represents the coverage of all source->value pairs, including those that are never observed."""

    def __init__(self, schema: Schema) -> None:
        all_vars: Set[VarInfo] = _import_var_pairs(schema)
        self._var_counts: Dict[VarInfo, int] = {var_info: 0 for var_info in all_vars}
        print("breakpoint")

    def merge_serialized_state(self, state_path: str) -> None:
        """Merge serialized state to combine results from child threads/processes."""

        with open(state_path, "rb") as f:
            var_indices: List[VarInfo]
            var_counts: Dict[int, int]
            var_indices, var_counts = pickle.load(f)
        for var_info_index, count in var_counts.items():
            try:
                var_info: VarInfo = var_indices[var_info_index]
            except KeyError as e:
                print("breakpoint")
                raise e

            try:
                self._var_counts[var_info] += count
            except KeyError as e:
                print("breakpoint")
                raise e

    def __len__(self) -> int:
        return len(self._var_counts)

    def __iter__(self) -> Iterator[VarInfo]:
        return self._var_counts.__iter__()

    def __getitem__(self, k: VarInfo) -> int:
        return self._var_counts[k]

