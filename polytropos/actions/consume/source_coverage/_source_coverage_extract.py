import json
import logging
import os
import uuid
from collections import defaultdict
from typing import Dict, Set, Tuple, List, Optional, Any

from polytropos.actions.consume.source_coverage._source_coverage_result import SourceCoverageResult
from polytropos.actions.consume.source_coverage._var_info import VarInfo
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable
from polytropos.tools.qc import POLYTROPOS_NA
from polytropos.util.paths import relpath_for


class SourceCoverageExtract:
    """Produces source coverage result for a chunk of composites.
    Can be called on separate process (all instance fields ard arguments/results of methods are serializable).
    """

    def __init__(self, schema: Schema, translate_dir: str, trace_dir: str, temp_dir: str):
        self.schema = schema
        self.translate_dir = translate_dir
        self.trace_dir = trace_dir
        self.temp_dir = temp_dir

    def _handle_keyed_list(self, composite_id: str, child_path: Tuple[str, ...], translate_value: Dict, trace_value: Dict,
                           observed: Dict[VarInfo, Set[Tuple[str, ...]]], all_vars: Set[VarInfo]) -> None:
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
                var_info = VarInfo(trace_value, child_var.var_id)
                if self.should_include_variable(var_info):
                    all_vars.add(var_info)

                    # Not count empty string, zero, or null as having been "observed."
                    # The boolean value `False` should still be counted.
                    if translate_value is not Ellipsis and (translate_value or translate_value is False):
                        observed[var_info].add(child_path)

    def _extract(self, translate_composite: Composite, trace_composite: Composite, result: SourceCoverageResult) -> None:
        composite_id = translate_composite.composite_id
        for period in trace_composite.content.keys():  # periods + "immutable"
            observed_paths: Dict[VarInfo, Set[Tuple[str, ...]]] = defaultdict(set)
            all_vars: Set[VarInfo] = set()
            self._crawl(composite_id, translate_composite.content.get(period, {}), trace_composite.content[period], (), observed_paths, all_vars)
            result.update(composite_id, period, all_vars, observed_paths)

    def extract(self, composite_ids: List[str]) -> str:
        """Produces source coverage result for a chunk of composites."""

        result = self.create_empty_result()
        for composite_id in composite_ids:
            logging.debug("Extracting data from composite %s", composite_id)

            translate_composite: Composite = self._load_composite(self.translate_dir, composite_id)
            trace_composite: Composite = self._load_composite(self.trace_dir, composite_id)
            self._extract(translate_composite, trace_composite, result)

        state_path = os.path.join(self.temp_dir, str(uuid.uuid4()))
        result.serialize_state(state_path)
        return state_path

    def create_empty_result(self) -> SourceCoverageResult:
        return SourceCoverageResult()

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

    def should_include_variable(self, var_info: VarInfo) -> bool:
        return True
