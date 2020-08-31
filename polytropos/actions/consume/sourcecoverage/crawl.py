import logging
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Optional, Any
from polytropos.actions.consume.sourcecoverage.pair import SourceTargetPair
from polytropos.actions.consume.sourcecoverage.result import SourceCoverageResult
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable
from polytropos.tools.qc import POLYTROPOS_NA

@dataclass
class Crawl:
    composite_id: str
    schema: Schema
    result: SourceCoverageResult = field(init=False, default_factory=SourceCoverageResult)

    def _handle_keyed_list(self, child_path: Tuple[str, ...], translate_value: Dict, trace_value: Dict) -> None:
        for key, trace_child_value in trace_value.items():
            translate_child_value = translate_value.get(key, {})
            self._crawl(translate_child_value, trace_child_value, child_path)

    def _handle_list(self, child_path: Tuple[str, ...], translate_value: List, trace_value: List) -> None:
        assert len(translate_value) == 0 or len(translate_value) == len(trace_value)
        for index, trace_child_value in enumerate(trace_value):
            translate_child_value = translate_value[index] if len(translate_value) > 0 else {}
            self._crawl(translate_child_value, trace_child_value, child_path)

    def _crawl(self, translate_content: Dict, trace_content: Dict, path: Tuple[str, ...]) -> None:

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

            # Exclude missing variable from the coverage report
            if child_var is None:
                continue

            # For known keyed lists, skip over the particular key names. Beyond this, we don't worry at this stage
            # whether the variable is known or not.
            if child_var.data_type == "KeyedList":
                assert isinstance(trace_value, dict)
                if translate_value is Ellipsis:
                    translate_value = {}
                else:
                    assert isinstance(translate_value, dict)

                self._handle_keyed_list(child_path, translate_value, trace_value)

            # For lists (except string lists), crawl each list item -- exclude string lists
            elif isinstance(trace_value, list) and not (
                    isinstance(translate_value, list) and len(trace_value) > 0 and isinstance(translate_value[0], str)):
                if translate_value is Ellipsis:
                    translate_value = []
                else:
                    assert isinstance(translate_value, list)

                self._handle_list(child_path, translate_value, trace_value)

            # If the value is a dict, and we do not it to be a keyed list, then we assume that it is a real folder.
            elif isinstance(trace_value, dict):
                if translate_value is Ellipsis:
                    translate_value = {}
                else:
                    if not isinstance(translate_value, dict):
                        logging.error("Expected a dict but got a {} in composite {}. Skipping.".format(
                            translate_value.__class__.__name__, self.composite_id))
                        return

                self._crawl(translate_value, trace_value, child_path)

            # In all other cases, the variable is a leaf node (primitive).
            else:
                pair: SourceTargetPair = SourceTargetPair(trace_value, child_var.var_id)

                # Not count empty string, zero, or null as having been "observed."
                # The boolean value `False` should still be counted.
                if translate_value is not Ellipsis and (translate_value or translate_value is False):
                    self.result.pair_counts[pair] += 1

    def __call__(self, translation: Dict, trace: Dict) -> SourceCoverageResult:
        for period in trace.keys():  # periods + "immutable"
            if period not in translation:
                logging.warning("Period {} is in the trace for {}, but not its translation.".format(period,
                                                                                                    self.composite_id))
            translate_content: Dict = translation.get(period, {})
            trace_content: Dict = trace[period]
            self._crawl(translate_content, trace_content, ())
        return self.result