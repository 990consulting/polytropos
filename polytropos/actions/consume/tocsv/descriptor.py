from dataclasses import field
from typing import Dict, Iterator, List

from polytropos.actions.consume.tocsv.valueset import ValueSet
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

class ColumnDescriptor:
    column_order: List[str]

    temporal_singletons: List[Dict] = field(default_factory=list)
    temporal_lists: List[Dict] = field(default_factory=list)
    temporal_named_lists: List[Dict] = field(default_factory=list)

    immutable_singletons: List[Dict] = field(default_factory=list)
    immutable_lists: List[Dict] = field(default_factory=list)
    immutable_named_lists: List[Dict] = field(default_factory=list)

    def __init__(self, schema: Schema, columns: List[Dict]):
        pass

    @property
    def colnames(self) -> Iterator[str]:
        """Returns the column names, as they should appear in the CSV header."""
        pass

    def _get_period_values(self, composite: Composite, period: str) -> ValueSet:
        # TODO This probably merits its own class with its own tests
        pass

    def _get_immutable_values(self, composite: Composite) -> ValueSet:
        # TODO This probably merits its own class with its own tests
        pass

    def _as_rows(self, i_vals: ValueSet, t_vals: ValueSet):
        # TODO This probably merits its own class with its own tests --> DO FIRST
        pass

    def _rows_for_period(self, composite: Composite, period: str, i_vals: ValueSet) -> Iterator[List]:
        t_vals = self._get_period_values(composite, period)
        yield from self._as_rows(i_vals, t_vals)

    def process(self, composite: Composite) -> Iterator[List]:
        i_vals: ValueSet = self._get_immutable_values(composite)

        for period in composite.periods:
            yield from self._rows_for_period(composite, period, i_vals)
