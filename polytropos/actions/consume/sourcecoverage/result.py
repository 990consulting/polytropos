import json
import pickle
from collections import Counter
from collections.abc import Mapping
from typing import Dict, Set, List, Optional, Iterator, Any, cast

from polytropos.actions.consume.sourcecoverage.pair import SourceTargetPair
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import VariableId, Variable

def _import_var_pairs(schema: Schema) -> Set[SourceTargetPair]:
    ret: Set[SourceTargetPair] = set()

    for target_var in schema:  # type: Variable
        if target_var.data_type in {"Folder", "List", "KeyedList"}:
            continue
        target_var_id: VariableId = target_var.var_id
        for source_var_id in target_var.sources:
            var_info: SourceTargetPair = SourceTargetPair(source_var_id, target_var_id)
            ret.add(var_info)
    return ret

class SourceCoverageResult:
    """Represents observed source->value pairs in a scan of the actual data."""

    def __init__(self) -> None:
        self.pair_counts: Counter = Counter()

    def update(self, other: "SourceCoverageResult") -> None:
        self.pair_counts += other.pair_counts

    def serialize_state(self, state_path: str) -> None:
        """Return serialized state to send it to the master process."""

        all_vars: List[SourceTargetPair] = list(self.pair_counts.keys())
        all_vars_indexes: Dict[SourceTargetPair, int] = {var_info: i for i, var_info in enumerate(all_vars)}
        var_counts: Dict[int, int] = {all_vars_indexes[var_info]: count for var_info, count in self.pair_counts.items()}
        with open(state_path, "wb") as f:
            pickle.dump((all_vars, var_counts), f)

    def __eq__(self, other: Optional[Any]) -> bool:
        if other is None or other.__class__ != self.__class__:
            return False
        if other.pair_counts != self.pair_counts:
            return False
        return True

    def __repr__(self) -> str:
        as_str: Dict = {str(pair): count for pair, count in self.pair_counts.items()}
        return json.dumps(as_str, default=str, indent=2)

class MergedSourceCoverageResult(Mapping):
    """Represents the coverage of all source->value pairs, including those that are never observed."""

    def __init__(self, schema: Schema) -> None:
        all_vars: Set[SourceTargetPair] = _import_var_pairs(schema)
        self._var_counts: Dict[SourceTargetPair, int] = {var_info: 0 for var_info in all_vars}

    def merge_serialized_state(self, state_path: str) -> None:
        """Merge serialized state to combine results from child threads/processes."""

        with open(state_path, "rb") as f:
            var_indices: List[SourceTargetPair]
            var_counts: Dict[int, int]
            var_indices, var_counts = pickle.load(f)

        for var_info_index, count in var_counts.items():
            var_info: SourceTargetPair = var_indices[var_info_index]
            try:
                self._var_counts[var_info] += count
            except KeyError as e:
                print("breakpoint")
                raise e

    def __len__(self) -> int:
        return len(self._var_counts)

    def __iter__(self) -> Iterator[SourceTargetPair]:
        return self._var_counts.__iter__()

    def __getitem__(self, k: SourceTargetPair) -> int:
        return self._var_counts[k]

