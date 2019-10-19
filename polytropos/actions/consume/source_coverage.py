import csv
import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Tuple, Any, Optional, Dict, Set, List, NamedTuple

from polytropos.ontology.context import Context
from polytropos.tools.qc import POLYTROPOS_NA
from polytropos.ontology.schema import Schema
from polytropos.util import nesteddicts
from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import Variable, VariableId
from polytropos.util.paths import relpath_for, find_all_composites


class VarInfo(NamedTuple):
    source_var_id: VariableId
    target_var_id: VariableId


class SourceCoverageFileExtractResult:
    def __init__(self) -> None:
        self.var_counts: Dict[VarInfo, int] = defaultdict(int)
        self.all_vars: Set[VarInfo] = set()

    def update(self, other: "SourceCoverageFileExtractResult") -> None:
        for var_info, count in other.var_counts.items():  # types: VarInfo, int
            self.var_counts[var_info] += count
        self.all_vars.update(other.all_vars)


@dataclass  # type: ignore # https://github.com/python/mypy/issues/5374
class SourceCoverageFile(Consume):
    translate_dir: str
    trace_dir: str

    coverage_result: SourceCoverageFileExtractResult = field(default_factory=SourceCoverageFileExtractResult, init=False)

    # noinspection PyTypeChecker
    @classmethod
    def standalone(cls, context: Context, translate_dir: str, trace_dir: str, source_schema_name: str, target_schema_name: str) -> None:
        source_schema: Optional[Schema] = Schema.load(source_schema_name, context.schemas_dir)
        assert source_schema is not None
        schema: Optional[Schema] = Schema.load(target_schema_name, context.schemas_dir, source_schema)
        assert schema is not None
        coverage: "SourceCoverageFile" = cls(context, schema, translate_dir, trace_dir)
        coverage("dummy", None)

    def before(self) -> None:
        pass

    def extract(self, composite: Composite) -> SourceCoverageFileExtractResult:
        raise NotImplementedError

    def consume(self, extracts: Iterable[Any]) -> None:
        for extract in extracts:
            self.coverage_result.update(extract)

    def _write_coverage_file(self) -> None:
        fn: str = os.path.join(self.context.output_dir, "source_coverage.csv")
        logging.info("Writing coverage file to %s.", fn)

        columns: List[str] = ["source_var_id", "source_var_path", "target_var_id", "target_var_path", "data_type", "n"]

        source_schema = self.schema.source
        assert source_schema is not None

        with open(fn, "w") as fh:
            writer: csv.DictWriter = csv.DictWriter(fh, columns)
            writer.writeheader()
            for var_info in sorted(self.coverage_result.all_vars):
                source_var_id = var_info.source_var_id
                target_var_id = var_info.target_var_id

                logging.debug("Writing coverage for %s -> %s.", source_var_id, target_var_id)
                source_var: Optional[Variable] = source_schema.get(source_var_id)
                target_var: Optional[Variable] = self.schema.get(target_var_id)
                assert source_var is not None and target_var is not None

                row = {
                    "source_var_id": source_var_id,
                    "source_var_path": nesteddicts.path_to_str(source_var.absolute_path),
                    "target_var_id": target_var_id,
                    "target_var_path": nesteddicts.path_to_str(target_var.absolute_path),
                    "data_type": source_var.data_type,
                    "n": self.coverage_result.var_counts.get(var_info, 0)
                }
                writer.writerow(row)

    def after(self) -> None:
        self._write_coverage_file()

    def process_composites(self, composite_ids: Iterable[str], origin_dir: str) -> Iterable[Any]:
        raise NotImplementedError

    def __call__(self, _origin_dir: str, _target_dir: Optional[str]) -> None:
        self.before()

        translate_composite_ids = set(find_all_composites(self.translate_dir))
        trace_composite_ids = set(find_all_composites(self.trace_dir))
        assert translate_composite_ids.issubset(trace_composite_ids)

        extract = SourceCoverageFileExtract(self.schema, self.translate_dir, self.trace_dir)
        per_composite_results: Iterable[SourceCoverageFileExtractResult] = self.context.run_in_process_pool(extract.extract, list(trace_composite_ids))

        self.consume(per_composite_results)
        self.after()


class SourceCoverageFileExtract:
    def __init__(self, schema: Schema, translate_dir: str, trace_dir: str):
        self.schema = schema
        self.translate_dir = translate_dir
        self.trace_dir = trace_dir

    def _handle_keyed_list(self, composite_id: str, child_path: Tuple[str, ...], translate_value: Dict, trace_value: Dict, observed: Dict[VarInfo, Set[Tuple[str, ...]]], all_vars: Set[VarInfo]) -> None:
        for key, trace_child_value in trace_value.items():
            translate_child_value = translate_value.get(key, {})
            self._crawl(composite_id, translate_child_value, trace_child_value, child_path, observed, all_vars)

    def _handle_list(self, composite_id: str, child_path: Tuple[str, ...], translate_value: List, trace_value: List, observed: Dict[VarInfo, Set[Tuple[str, ...]]], all_vars: Set[VarInfo]) -> None:
        assert len(translate_value) == 0 or len(translate_value) == len(trace_value)
        for index, trace_child_value in enumerate(trace_value):
            translate_child_value = translate_value[index] if len(translate_value) > 0 else {}
            self._crawl(composite_id, translate_child_value, trace_child_value, child_path, observed, all_vars)

    def _crawl(self, composite_id: str, translate_content: Dict, trace_content: Dict, path: Tuple[str, ...], observed: Dict[VarInfo, Set[Tuple[str, ...]]], all_vars: Set[VarInfo]) -> None:
        for key, trace_value in trace_content.items():  # type: str, Any
            # Ignore system variables
            if key[0] == "_":
                continue

            translate_value = translate_content.get(key, Ellipsis)

            # Ignore explicit NAs (which occur in "expected value" test fixtures), but not None. The former is used to
            # indicate explicitly that a variable was not included at all in the actual values, and so does not
            # contribute to test coverage. In order for a None value to appear, it had to be explicitly supplied in the
            # source, which means that it *is* a meaningful value.
            if translate_value == POLYTROPOS_NA:
                continue

            child_path: Tuple[str, ...] = path + (key,)

            # Micro-optimization - direct access to a protected member
            # noinspection PyProtectedMember
            child_var: Optional[Variable] = self.schema._var_path_cache.get(child_path)

            # Exclude missing or transient variable from the coverage report
            if child_var is None or child_var.transient:
                continue

            # For known keyed lists, skip over the particular key names. Beyond this, we don't worry at this stage
            # whether the variable is known or not.
            if child_var.data_type == "KeyedList":
                assert isinstance(trace_value, dict)
                if translate_value is Ellipsis:
                    translate_value = {}
                else:
                    assert isinstance(translate_value, dict)

                self._handle_keyed_list(composite_id, child_path, translate_value, trace_value, observed, all_vars)

            # For lists (except string lists), crawl each list item -- exclude string lists
            elif isinstance(trace_value, list) and not (isinstance(translate_value, list) and len(trace_value) > 0 and isinstance(translate_value[0], str)):
                if translate_value is Ellipsis:
                    translate_value = []
                else:
                    assert isinstance(translate_value, list)

                self._handle_list(composite_id, child_path, translate_value, trace_value, observed, all_vars)

            # If the value is a dict, and we do not it to be a keyed list, then we assume that it is a real folder.
            elif isinstance(trace_value, dict):
                if translate_value is Ellipsis:
                    translate_value = {}
                else:
                    assert isinstance(translate_value, dict)

                self._crawl(composite_id, translate_value, trace_value, child_path, observed, all_vars)

            # In all other cases, the variable is a leaf node (primitive).
            else:
                var_info = VarInfo(source_var_id=trace_value, target_var_id=child_var.var_id)
                all_vars.add(var_info)

                # Not empty string, zero, or null as having been "observed."
                # The boolean value `False` should still be counted.
                if translate_value is not Ellipsis and (translate_value or translate_value is False):
                    observed[var_info].add(child_path)

    def _extract(self, translate_composite: Composite, trace_composite: Composite, result: SourceCoverageFileExtractResult) -> None:
        for period in trace_composite.content.keys():  # periods + "immutable"
            observed_paths: Dict[VarInfo, Set[Tuple[str, ...]]] = defaultdict(set)
            all_vars: Set[VarInfo] = set()
            self._crawl(translate_composite.composite_id, translate_composite.content.get(period, {}), trace_composite.content[period], (), observed_paths, all_vars)
            for var_info, target_paths in observed_paths.items():
                result.var_counts[var_info] += len(target_paths)
            result.all_vars.update(all_vars)

    def extract(self, composite_ids: List[str]) -> SourceCoverageFileExtractResult:
        extract_result = SourceCoverageFileExtractResult()
        for composite_id in composite_ids:
            logging.debug("Extracting data from composite %s", composite_id)

            translate_composite: Composite = self._load_composite(self.translate_dir, composite_id)
            trace_composite: Composite = self._load_composite(self.trace_dir, composite_id)
            self._extract(translate_composite, trace_composite, extract_result)

        return extract_result

    def _load_composite(self, base_dir: str, composite_id: str) -> Composite:
            relpath: str = relpath_for(composite_id)
            composite_path = os.path.join(base_dir, relpath, "%s.json" % composite_id)
            content: Dict
            if not os.path.exists(composite_path):
                content = {}
            else:
                with open(os.path.join(base_dir, relpath, "%s.json" % composite_id)) as translate_file:
                    content = json.load(translate_file)
            return Composite(self.schema, content, composite_id=composite_id)
