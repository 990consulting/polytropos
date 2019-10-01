import csv
import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Tuple, Any, Optional, Dict, Set, List

from polytropos.ontology.context import Context
from polytropos.tools.qc import POLYTROPOS_NA

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track
from polytropos.util import nesteddicts

from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable, VariableId
from polytropos.util.paths import relpath_for


def _get_sorted_vars(group_var_counts: Dict[Optional[str], Dict[Tuple[str, ...], int]], track: Track) \
        -> List[Tuple[str, ...]]:
    all_known_vars: Set[Tuple[str, ...]] = set()
    for counter in group_var_counts.values():
        for key in counter:
            all_known_vars.add(key)
    for variable in track.values():
        # Exclude transient variable from the coverage report
        if not (variable.transient or variable.has_transient_ancestor):
            path: Tuple[str, ...] = tuple(variable.absolute_path)
            all_known_vars.add(path)
    sorted_vars: List[Tuple[str, ...]] = sorted(all_known_vars)
    return sorted_vars


class CoverageFileExtractResult:
    def __init__(self) -> None:
        # Count of observations of each variable path by grouping variable
        self.temporal_var_counts: Dict[Optional[str], Dict[Tuple[str, ...], int]] = defaultdict(dict)
        self.immutable_var_counts: Dict[Optional[str], Dict[Tuple[str, ...], int]] = defaultdict(dict)

        # Number of times each value of the grouping variable was observed
        self.temporal_n: Dict[Optional[str], int] = defaultdict(int)
        self.immutable_n: Dict[Optional[str], int] = defaultdict(int)

    def update(self, other: "CoverageFileExtractResult") -> None:
        for group, counts in other.temporal_var_counts.items():  # types: Optional[str], dict
            for path, count in counts.items():
                self.temporal_var_counts.setdefault(group, defaultdict(int))[path] += count
        for group, counts in other.immutable_var_counts.items():  # types: Optional[str], dict
            for path, count in counts.items():
                self.immutable_var_counts.setdefault(group, defaultdict(int))[path] += count

        for group, count in other.temporal_n.items():  # types: Optional[str], int
            self.temporal_n[group] += count
        for group, count in other.immutable_n.items():  # types: Optional[str], int
            self.immutable_n[group] += count


@dataclass
class CoverageFile(Consume):
    """Iterates over all periods in all composites, optionally classifying them according to a grouping variable. Within
    each group, count the number of times records for which a given variable path occurred at least once, as well as
    the number of observations. Produce a normalized report indicating the percentage of observations within each group
    that had a given variable path. Also indicate whether the variable path exists in the schema. System variables
    (which start with an underscore or descend from a variable with an underscore) are ignored.

    Produces two files: one for temporal observations, and one for immutable observations."""

    file_prefix: str
    temporal_grouping_var: Optional[VariableId] = field(default=None)
    immutable_grouping_var: Optional[VariableId] = field(default=None)
    exclude_trivial: bool = False

    coverage_result: CoverageFileExtractResult = field(default_factory=CoverageFileExtractResult, init=False)

    # noinspection PyTypeChecker
    @classmethod
    def standalone(cls, context: Context, schema_name: str, output_prefix: str,
                   t_group: Optional[VariableId], i_group: Optional[VariableId], exclude_trivial: bool = False) -> None:

        schema: Optional[Schema] = Schema.load(schema_name, context.schemas_dir)
        assert schema is not None
        # TODO Refactor so unnecessary arguments aren't required.
        coverage: "CoverageFile" = cls(context, schema, output_prefix, t_group, i_group, exclude_trivial)
        coverage(context.entities_input_dir, None)

    def before(self) -> None:
        logging.info("Validating grouping variables (if any).")
        if self.temporal_grouping_var is not None and self.schema.get(self.temporal_grouping_var) is None:
            raise ValueError('Temporal grouping variable "%s" does not exist.')
        if self.immutable_grouping_var is not None and self.schema.get(self.immutable_grouping_var) is None:
            raise ValueError('Immutable grouping variable "%s" does not exist.')

    def extract(self, composite: Composite) -> CoverageFileExtractResult:
        raise NotImplementedError

    def consume(self, extracts: Iterable[Any]) -> None:
        for extract in extracts:
            self.coverage_result.update(extract)

    def _init_row(self, var_path: Tuple) -> Dict:
        var_path_str: str = nesteddicts.path_to_str(var_path)
        var: Optional[Variable] = self.schema.lookup(var_path)
        if var is not None:
            return {
                "variable": var_path_str,
                "in_schema": "TRUE",
                "var_id": var.var_id,
                "data_type": var.data_type
            }
        else:
            return {
                "variable": var_path_str,
                "in_schema": "FALSE",
                "var_id": "",
                "data_type": ""
            }

    def _write_groups_file(self, group_obs_counts: Dict[Optional[str], int], grouping_var_id: Optional[str],
                           infix: str) -> None:
        groups_fn: str = self.file_prefix + "_" + infix + "_groups.csv"
        logging.info("Writing groups file to %s.", groups_fn)

        with open(groups_fn, "w") as fh:
            group_var_path: str = "Group"
            if grouping_var_id is not None:
                group_var: Optional[Variable] = self.schema.lookup(grouping_var_id)
                if group_var is not None:
                    group_var_path = nesteddicts.path_to_str(group_var.absolute_path)

            writer: csv.DictWriter = csv.DictWriter(fh, [group_var_path, "observations"])
            writer.writeheader()
            for key, value in sorted(zip([str(key) for key in group_obs_counts.keys()], group_obs_counts.values())):
                writer.writerow({
                    group_var_path: str(key),
                    "observations": str(value)
                })

    def _write_coverage_file(self, track: Track, group_obs_counts: Dict[Optional[str], int],
                             group_var_counts: Dict[Optional[str], Dict[Tuple[str, ...], int]], infix: str) -> None:
        fn: str = self.file_prefix + "_" + infix + ".csv"
        logging.info("Writing coverage file to %s.", fn)

        groups: List[str] = sorted([str(x) for x in group_obs_counts.keys()])
        columns: List[str] = ["variable", "in_schema", "var_id", "data_type"] + groups
        sorted_vars = _get_sorted_vars(group_var_counts, track)

        with open(fn, "w") as fh:
            writer: csv.DictWriter = csv.DictWriter(fh, columns)
            writer.writeheader()
            for var_path in sorted_vars:
                logging.debug("Writing coverage for %s.", nesteddicts.path_to_str(var_path))
                row: Dict = self._init_row(var_path)
                for group in group_obs_counts.keys():
                    n_in_group: int = group_obs_counts[group]
                    times_var_observed: int = group_var_counts[group].get(var_path, 0)
                    frac: float = times_var_observed / n_in_group
                    if frac > 1.0:
                        logging.warning("Observed coverage of {:.5f} (>1) for variable {:}."
                                        .format(frac, nesteddicts.path_to_str(var_path)))
                    #assert frac <= 1.0
                    row[str(group)] = "%0.2f" % frac
                writer.writerow(row)

    def _write(self, track: Track, infix: str, group_var_counts: Dict[Optional[str], Dict[Tuple[str, ...], int]],
               group_obs_counts: Dict[Optional[str], int], grouping_var_id: Optional[str]) -> None:

        self._write_coverage_file(track, group_obs_counts, group_var_counts, infix)
        self._write_groups_file(group_obs_counts, grouping_var_id, infix)

    def _write_temporal(self) -> None:
        self._write(self.schema.temporal, "temporal", self.coverage_result.temporal_var_counts,
                    self.coverage_result.temporal_n, self.temporal_grouping_var)

    def _write_immutable(self) -> None:
        self._write(self.schema.immutable, "immutable", self.coverage_result.immutable_var_counts,
                    self.coverage_result.immutable_n, self.immutable_grouping_var)

    def after(self) -> None:
        self._write_temporal()
        self._write_immutable()

    def process_composites(self, composite_ids: Iterable[str], origin_dir: str) -> Iterable[Any]:
        extract = CoverageFileExtract(self.schema, origin_dir, self.temporal_grouping_var, self.immutable_grouping_var, self.exclude_trivial)
        return self.context.run_in_process_pool(extract.extract, list(composite_ids))


class CoverageFileExtract:
    def __init__(self, schema: Schema, origin_dir: str, temporal_grouping_var: Optional[VariableId], immutable_grouping_var: Optional[VariableId], exclude_trivial: bool):
        self.schema = schema
        self.origin_dir = origin_dir
        self.temporal_grouping_var = temporal_grouping_var
        self.immutable_grouping_var = immutable_grouping_var
        self.exclude_trivial = exclude_trivial

    def _get_temporal_group(self, composite: Composite, period: str) -> Optional[str]:
        if self.temporal_grouping_var is None:
            return None
        return composite.get_observation(self.temporal_grouping_var, period, treat_missing_as_null=True)

    def _get_immutable_group(self, composite: Composite) -> Optional[str]:
        if self.immutable_grouping_var is None:
            return None
        return composite.get_immutable(self.immutable_grouping_var, treat_missing_as_null=True)

    def _handle_keyed_list(self, composite_id: str, child_path: Tuple[str, ...], value: Any, observed: Set) -> None:
        for child_value in value.values():
            if child_value is None:
                logging.debug("Encountered empty keyed list item in composite %s (path %s).", composite_id,
                              nesteddicts.path_to_str(child_path))
                continue
            self._crawl(composite_id, child_value, observed, child_path)

    def _handle_list(self, composite_id: str, child_path: Tuple[str, ...], value: Any, observed: Set) -> None:
        for child_value in value:
            if child_value is None:
                logging.debug("Encountered empty list item in composite %s (path %s).", composite_id,
                              nesteddicts.path_to_str(child_path))
                continue
            self._crawl(composite_id, child_value, observed, child_path)

    def _crawl(self, composite_id: str, content: Dict, observed: Set[Tuple], path: Tuple[str, ...]) -> None:
        for key, value in content.items():  # type: str, Any
            # Ignore system variables
            if key[0] == "_":
                continue

            # Ignore explicit NAs (which occur in "expected value" test fixtures), but not None. The former is used to
            # indicate explicitly that a variable was not included at all in the actual values, and so does not
            # contribute to test coverage. In order for a None value to appear, it had to be explicitly supplied in the
            # source, which means that it *is* a meaningful value.
            if value == POLYTROPOS_NA:
                continue

            if self.exclude_trivial:
                # Not count empty dictionary, empty list, empty string, zero, or null as having been "observed."
                # The boolean value `False` should still be counted.
                if not value and value is not False:
                    continue

            child_path: Tuple[str, ...] = path + (key,)

            # Micro-optimization - direct access to a protected member
            # noinspection PyProtectedMember
            child_var: Optional[Variable] = self.schema._var_path_cache.get(child_path)

            # Exclude transient variable from the coverage report
            if child_var is not None and child_var.transient:
                continue

            # Record that we saw this path
            observed.add(child_path)

            # For known keyed lists, skip over the particular key names. Beyond this, we don't worry at this stage
            # whether the variable is known or not.

            if child_var is not None and child_var.data_type == "KeyedList":
                self._handle_keyed_list(composite_id, child_path, value, observed)

            # For lists (except string lists), crawl each list item -- exclude string lists
            elif isinstance(value, list) and not (len(value) > 0 and isinstance(value[0], str)):
                self._handle_list(composite_id, child_path, value, observed)

            # If the value is a dict, and we do not it to be a keyed list, then we assume that it is a real folder.
            elif isinstance(value, dict):
                self._crawl(composite_id, value, observed, child_path)

            # In all other cases, the variable is a leaf node (primitive), so no further action needed.

    def _extract_temporal(self, composite: Composite, result: CoverageFileExtractResult) -> None:
        """For each grouping variable value, get a count of the number of OBSERVATIONS with AT LEAST ONE instance of a
        given variable. That is, if a variable is nested inside a list and happens 100 times, it only counts once; but
        if this happens in two different observations within the same composite, and both observations have the same
        grouping variable value, then the count for that group/variable combo is 2."""
        for period in composite.periods:
            group: Optional[str] = self._get_temporal_group(composite, period)
            result.temporal_n[group] += 1
            observed: Set[Tuple] = set()
            self._crawl(composite.composite_id, composite.content[period], observed, ())
            for path in observed:
                result.temporal_var_counts.setdefault(group, defaultdict(int))[path] += 1

    def _extract_immutable(self, composite: Composite, result: CoverageFileExtractResult) -> None:
        """Note that this will always return a dictionary of length 0 or 1, but using a Dict simplifies code due to
        analogy with _extract_temporal."""
        if "immutable" not in composite.content:
            return

        group: Optional[Optional[str]] = self._get_immutable_group(composite)
        result.immutable_n[group] += 1
        observed: Set[Tuple] = set()
        self._crawl(composite.composite_id, composite.content["immutable"], observed, ())
        if len(observed) == 0:
            return

        for path in observed:
            result.immutable_var_counts.setdefault(group, defaultdict(int))[path] += 1

    def extract(self, composite_ids: List[str]) -> CoverageFileExtractResult:
        extract_result = CoverageFileExtractResult()
        for composite_id in composite_ids:
            logging.debug("Extracting data from composite %s", composite_id)

            relpath: str = relpath_for(composite_id)
            with open(os.path.join(self.origin_dir, relpath, "%s.json" % composite_id)) as origin_file:
                content: Dict = json.load(origin_file)
            composite: Composite = Composite(self.schema, content, composite_id=composite_id)

            self._extract_temporal(composite, extract_result)
            self._extract_immutable(composite, extract_result)
        return extract_result
