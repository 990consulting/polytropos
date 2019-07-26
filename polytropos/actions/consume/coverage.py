import csv
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Iterable, Tuple, Any, Optional, Dict, NamedTuple, Set, List

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track
from polytropos.util import nesteddicts

from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable

def _get_sorted_vars(group_var_counts: Dict[str, Counter], track: Track):
    all_known_vars: Set[Tuple] = set()
    for counter in group_var_counts.values():
        for key in counter:
            all_known_vars.add(key)
    for variable in track.values():
        path: Tuple = tuple(variable.absolute_path)
        all_known_vars.add(path)
    sorted_vars: List[Tuple] = sorted(all_known_vars)
    return sorted_vars

@dataclass
class CoverageFile(Consume):
    """Iterates over all periods in all composites, optionally classifying them according to a grouping variable. Within
    each group, count the number of times records for which a given variable path occurred at least once, as well as
    the number of observations. Produce a normalized report indicating the percentage of observations within each group
    that had a given variable path. Also indicate whether the variable path exists in the schema. System variables
    (which start with an underscore or descend from a variable with an underscore) are ignored.

    Produces two files: one for temporal observations, and one for immutable observations."""

    file_prefix: str
    temporal_grouping_var: Optional[str] = field(default=None)
    immutable_grouping_var: Optional[str] = field(default=None)

    # Count of observations of each variable path by grouping variable
    temporal_var_counts: Dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter), init=False)
    immutable_var_counts: Dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter), init=False)

    # Number of times each value of the grouping variable was observed
    temporal_n: Dict[str, int] = field(default_factory=lambda: defaultdict(int), init=False)
    immutable_n: Dict[str, int] = field(default_factory=lambda: defaultdict(int), init=False)

    # noinspection PyTypeChecker
    @classmethod
    def standalone(cls, schema_basepath: str, schema_name: str, data_path: str, output_prefix: str,
                   t_group: str, i_group: str):

        schema: Schema = Schema.load(schema_name, base_path=schema_basepath)
        # TODO Refactor so unnecessary arguments aren't required.
        coverage: "CoverageFile" = cls(None, schema, output_prefix, t_group, i_group)
        coverage(data_path, None)

    def before(self):
        if self.temporal_grouping_var is not None and self.schema.get(self.temporal_grouping_var) is None:
            raise ValueError('Temporal grouping variable "%s" does not exist.')
        if self.immutable_grouping_var is not None and self.schema.get(self.immutable_grouping_var) is None:
            raise ValueError('Immutable grouping variable "%s" does not exist.')

    def _get_temporal_group(self, composite: Composite, period: str) -> Optional[str]:
        if self.temporal_grouping_var is None:
            return None
        return composite.get_observation(self.temporal_grouping_var, period, treat_missing_as_null=True)

    def _get_immutable_group(self, composite: Composite) -> Optional[str]:
        if self.immutable_grouping_var is None:
            return None
        return composite.get_immutable(self.immutable_grouping_var, treat_missing_as_null=True)

    def _crawl(self, content: Dict, observed: Set[Tuple], path: List):
        for key, value in content.items():  # type: str, Any
            # Ignore system variables
            if key.startswith("_"):
                continue

            # Record that we saw this path
            child_path: List = path + [key]
            observed.add(tuple(child_path))

            # For known named lists, skip over the particular key names. Beyond this, we don't worry at this stage
            # whether the variable is known or not.
            child_var: Variable = self.schema.lookup(child_path)
            if child_var and child_var.data_type == "NamedList":
                for child_value in value.values():
                    self._crawl(child_value, observed, child_path)

            # For lists, crawl each list item
            elif isinstance(value, list):
                for child_value in value:
                    self._crawl(child_value, observed, child_path)

            # If the value is a dict, and we do not it to be a named list, then we assume that it is a real folder.
            elif isinstance(value, dict):
                self._crawl(value, observed, child_path)

            # In all other cases, the variable is a leaf node (primitive), so no further action needed.

    def _extract_temporal(self, composite: Composite) -> Dict[str, Counter]:
        """For each grouping variable value, get a count of the number of OBSERVATIONS with AT LEAST ONE instance of a
        given variable. That is, if a variable is nested inside a list and happens 100 times, it only counts once; but
        if this happens in two different observations within the same composite, and both observations have the same
        grouping variable value, then the count for that group/variable combo is 2."""
        ret: Dict[str, Counter] = defaultdict(Counter)
        for period in composite.periods:
            group: Optional[str] = self._get_temporal_group(composite, period)
            self.temporal_n[group] += 1
            observed: Set[Tuple] = set()
            self._crawl(composite.content[period], observed, [])
            for path in observed:
                ret[group][path] += 1
        return ret

    def _extract_immutable(self, composite: Composite) -> Dict[str, Counter]:
        """Note that this will always return a dictionary of length 0 or 1, but using a Dict simplifies code due to
        analogy with _extract_temporal."""
        if "immutable" not in composite.content:
            return {}

        group: Optional[str] = self._get_immutable_group(composite)
        self.immutable_n[group] += 1
        observed: Set[Tuple] = set()
        self._crawl(composite.content["immutable"], observed, [])
        if len(observed) == 0:
            return {}

        counts: Counter = Counter()
        for path in observed:
            counts[path] += 1
        return {group: counts}

    def extract(self, composite: Composite) -> Tuple[Dict[str, Counter], Dict[str, Counter]]:
        temporal_counts: Dict[str, Counter] = self._extract_temporal(composite)
        immutable_counts: Dict[str, Counter] = self._extract_immutable(composite)
        return temporal_counts, immutable_counts

    def consume(self, extracts: Iterable[Tuple[str, Tuple[Dict[str, Counter], Dict[str, Counter]]]]) -> None:
        for filename, extract in extracts:
            # Incorporate temporal data
            temporal_counts, immutable_counts = extract
            for group, counts in temporal_counts.items():  # types: Optional[str], Counter
                self.temporal_var_counts[group] += counts
            for group, counts in immutable_counts.items():
                self.immutable_var_counts[group] += counts

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

    def _write_groups_file(self, group_obs_counts: Dict[str, int], grouping_var_id: str, infix: str):
        groups_fn: str = self.file_prefix + "_" + infix + "_groups.csv"
        with open(groups_fn, "w") as fh:
            group_var_path: str = "Group"
            if grouping_var_id is not None:
                group_var: Variable = self.schema.lookup(grouping_var_id)
                if group_var is not None:
                    group_var_path: str = nesteddicts.path_to_str(group_var.absolute_path)

            writer: csv.DictWriter = csv.DictWriter(fh, [group_var_path, "observations"])
            writer.writeheader()
            for key, value in sorted(zip([str(key) for key in group_obs_counts.keys()], group_obs_counts.values())):
                writer.writerow({
                    group_var_path: str(key),
                    "observations": str(value)
                })

    def _write_coverage_file(self, track: Track, group_obs_counts: Dict[str, int],
                             group_var_counts: Dict[str, Counter], infix: str):
        groups: List[str] = sorted([str(x) for x in group_var_counts.keys()])
        columns: List[str] = ["variable", "in_schema", "var_id", "data_type"] + groups
        sorted_vars = _get_sorted_vars(group_var_counts, track)

        fn: str = self.file_prefix + "_" + infix + ".csv"
        with open(fn, "w") as fh:
            writer: csv.DictWriter = csv.DictWriter(fh, columns)
            writer.writeheader()
            for var_path in sorted_vars:
                row: Dict = self._init_row(var_path)
                for group in group_obs_counts.keys():
                    n_in_group: int = group_obs_counts[group]
                    times_var_observed: int = group_var_counts[group][var_path]
                    frac: float = times_var_observed / n_in_group
                    assert frac <= 1.0
                    row[str(group)] = "%0.2f" % frac
                writer.writerow(row)

    def _write(self, track: Track, infix: str, group_var_counts: Dict[str, Counter], group_obs_counts: Dict[str, int],
               grouping_var_id: str):

        self._write_coverage_file(track, group_obs_counts, group_var_counts, infix)
        self._write_groups_file(group_obs_counts, grouping_var_id, infix)

    def _write_temporal(self):
        self._write(self.schema.temporal, "temporal", self.temporal_var_counts, self.temporal_n,
                    self.temporal_grouping_var)

    def _write_immutable(self):
        self._write(self.schema.immutable, "immutable", self.immutable_var_counts, self.immutable_n,
                    self.immutable_grouping_var)

    def after(self):
        self._write_temporal()
        self._write_immutable()
