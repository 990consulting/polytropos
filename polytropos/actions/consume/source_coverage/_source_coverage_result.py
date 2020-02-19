import pickle
from collections import defaultdict
from typing import Dict, Set, Tuple, List, cast

from polytropos.actions.consume.source_coverage._var_info import VarInfo


class SourceCoverageResult:
    """Represents result of source coverage.
       all_vars: a list of available source/target variables
       var_counts: how many times each source/target pair is covered
    """

    def __init__(self) -> None:
        self.all_vars: Set[VarInfo] = set()
        self.var_counts: Dict[VarInfo, int] = defaultdict(int)

    def update(self, composite_id: str, period: str, all_vars: Set[VarInfo], observed_paths: Dict[VarInfo, Set[Tuple[str, ...]]]) -> None:
        """Update the result with new data from given ein/period."""

        for var_info, target_paths in observed_paths.items():
            assert len(target_paths) == 1
            self.var_counts[var_info] += 1
        self.all_vars.update(all_vars)

    def serialize_state(self) -> bytes:
        """Return serialized state to send it to the master process."""

        all_vars: List[VarInfo] = list(self.all_vars)
        all_vars_indexes: Dict[VarInfo, int] = {var_info: i for i, var_info in enumerate(all_vars)}
        var_counts: Dict[int, int] = {all_vars_indexes[var_info]: count for var_info, count in self.var_counts.items()}
        return pickle.dumps((all_vars, var_counts))

    def merge_serialized_state(self, state: bytes) -> None:
        """Merge serialized state to combine results from child threads/processes."""

        all_vars, var_counts = cast(Tuple[List[VarInfo], Dict[int, int]], pickle.loads(state))
        for var_info_index, count in var_counts.items():  # types: int, int
            self.var_counts[all_vars[var_info_index]] += count
        self.all_vars.update(all_vars)
