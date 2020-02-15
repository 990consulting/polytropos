from collections import defaultdict
from typing import Dict, Set, Tuple

from polytropos.actions.consume.source_coverage._var_info import VarInfo


class SourceCoverageResult:
    """Represents result of source coverage.
       all_vars: a list of available source/target variables
       var_counts: how many times each source/target pair is covered
    """

    def __init__(self) -> None:
        self.all_vars: Set[VarInfo] = set()
        self.var_counts: Dict[VarInfo, int] = defaultdict(int)

    def merge(self, other: "SourceCoverageResult") -> None:
        """Merge two results (used to combine results from separate threads/processes to summary result)."""

        for var_info, count in other.var_counts.items():  # types: VarInfo, int
            self.var_counts[var_info.interned()] += count
        self.all_vars.update((var_info.interned() for var_info in other.all_vars))

    def update(self, composite_id: str, period: str, all_vars: Set[VarInfo], observed_paths: Dict[VarInfo, Set[Tuple[str, ...]]]) -> None:
        """Update the result with new data from given ein/period."""

        for var_info, target_paths in observed_paths.items():
            assert len(target_paths) == 1
            self.var_counts[var_info] += 1
        self.all_vars.update(all_vars)
