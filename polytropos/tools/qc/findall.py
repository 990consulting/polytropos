import json
import logging
import os
from typing import Dict, Set, Optional, Iterator, List

from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema
from polytropos.tools.qc.compare import FixtureComparator

from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch, MissingValue

def _get_composite(path: str, entity_id: str, schema: Schema) -> Optional[Composite]:
    filename: str = "%s/%s.json" % (path, entity_id)
    if not os.path.exists(filename):
        return None
    with open(filename) as fh:
        content: Dict = json.load(fh)
    return Composite(schema, content, composite_id=entity_id)

class FixtureOutcomes:
    def __init__(self, schema: Schema, fixture_path: str, actual_path: str):
        unsorted_outcomes: Dict[str, Outcome] = {}
        self.no_actual: Set[str] = set()

        for filename in os.listdir(fixture_path):
            if not filename.endswith(".json") or filename.startswith("."):
                logging.warning("Skipping non-fixture file %s." % filename)
                continue
            entity_id: str = filename[:-5]  # Strip off the ".json"
            actual: Optional[Composite] = _get_composite(actual_path, entity_id, schema)
            if actual is None:
                self.no_actual.add(entity_id)
                logging.warning("No actual value observed for fixture %s." % entity_id)
                continue
            fixture: Composite = _get_composite(fixture_path, entity_id, schema)
            assert fixture is not None
            comparator: FixtureComparator = FixtureComparator(schema, entity_id, fixture, actual)
            outcome: Outcome = comparator.outcome
            unsorted_outcomes[entity_id] = outcome

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
