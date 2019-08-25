import json
import logging
import os
from typing import Dict, Set, Optional, Iterator, List

from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.tools.qc.compare import FixtureComparator

from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch, MissingValue
from polytropos.util.paths import find_all_composites, relpath_for

def _get_composite(basepath: str, composite_id: str, schema: Schema) -> Optional[Composite]:
    relpath: str = relpath_for(composite_id)
    filename: str = os.path.join(basepath, relpath, "%s.json" % composite_id)
    if not os.path.exists(filename):
        return None
    with open(filename) as fh:
        try:
            content: Dict = json.load(fh)
        except Exception as e:
            logging.error("Error reading composite %s" % filename)
            raise e
    return Composite(schema, content, composite_id=composite_id)

class FixtureOutcomes:
    def __init__(self, schema: Schema, fixture_path: str, actual_path: str):
        unsorted_outcomes: Dict[str, Outcome] = {}
        self.no_actual: Set[str] = set()

        for composite_id in find_all_composites(fixture_path):
            actual: Optional[Composite] = _get_composite(actual_path, composite_id, schema)
            if actual is None:
                self.no_actual.add(composite_id)
                logging.warning("No actual value observed for fixture %s." % composite_id)
                continue
            fixture: Optional[Composite] = _get_composite(fixture_path, composite_id, schema)
            assert fixture is not None
            comparator: FixtureComparator = FixtureComparator(schema, composite_id, fixture, actual)
            outcome: Outcome = comparator.outcome
            unsorted_outcomes[composite_id] = outcome

        self.outcomes: List = [unsorted_outcomes[key] for key in sorted(unsorted_outcomes.keys())]

    @property
    def matches(self) -> Iterator[ValueMatch]:
        for outcome in self.outcomes:
            yield from outcome.matches

    @property
    def match_ids(self) -> Iterator[str]:
        for outcome in self.outcomes:
            yield from outcome.match_case_ids

    @property
    def mismatches(self) -> Iterator[ValueMismatch]:
        for outcome in self.outcomes:
            yield from outcome.mismatches

    @property
    def mismatch_ids(self) -> Iterator[str]:
        for outcome in self.outcomes:
            yield from outcome.mismatch_case_ids

    @property
    def missing_values(self) -> Iterator[MissingValue]:
        for outcome in self.outcomes:
            yield from outcome.missings

    @property
    def missing_value_ids(self) -> Iterator[str]:
        for outcome in self.outcomes:
            yield from outcome.missing_case_ids
