from typing import Optional, Any

from polytropos.util.nesteddicts import MissingDataError

from polytropos.actions.filter.multivariate.__multivariate import SpecificValuesFilter
from polytropos.ontology.composite import Composite

class HasAnySpecificValues(SpecificValuesFilter):
    """OR logic for filtering and narrowing (may be used for either or both).

    Filtering: Includes only records that have ever had a period in which at least one of the specified fields had
    the specified value. If one of the specified values is an immutable value, having that value will cause the record
    to pass.

    Narrowing: Includes only periods in which at least one of the specified fields has the specified value. Immutable
    values count against all periods; i.e., if an immutable value matches, all periods will be included."""

    def temporals_pass(self, composite: Composite, period: str) -> bool:
        for var_id in self.temporal_vars:
            try:
                actual: Optional[Any] = composite.get_observation(var_id, period)
            except MissingDataError:
                continue
            if actual == self.expected[var_id]:
                return True
        return False

    def immutables_pass(self, composite: Composite) -> bool:
        for var_id in self.immutable_vars:
            try:
                actual: Optional[Any] = composite.get_immutable(var_id)
            except MissingDataError:
                continue
            if actual == self.expected[var_id]:
                return True
        return False

    def passes(self, composite: Composite) -> bool:
        if not self.filters:
            return True

        if self.immutables_pass(composite):
            return True
        for period in composite.periods:
            if self.temporals_pass(composite, period):
                return True
        return False

    def narrow(self, composite: Composite) -> None:
        if not self.narrows:
            return

        if len(self.immutable_vars) > 0 and self.immutables_pass(composite):
            return

        else:
            for period in composite.periods:
                if not self.temporals_pass(composite, period):
                    del composite.content[period]
