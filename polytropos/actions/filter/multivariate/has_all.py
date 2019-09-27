from typing import Optional, Any

from polytropos.actions.filter.multivariate.__multivariate import SpecificValuesFilter
from polytropos.ontology.composite import Composite
from polytropos.util.nesteddicts import MissingDataError

class HasAllSpecificValues(SpecificValuesFilter):
    """AND logic for filtering and narrowing (may be used for either or both).

    Filtering: Includes only records that have ever had a period in which each specified field had the specified
    value. All temporal fields specified must have had the specified value in the same period (temporal variables are
    checked against all periods).

    Narrowing: Includes only periods in which each specified field has the specified value. Immutable values count
    against all periods; i.e., if an immutable value is incorrect, the composite will be emptied.
    """

    def temporals_pass(self, composite: Composite, period: str) -> bool:
        for var_id in self.temporal_vars:
            try:
                actual: Optional[Any] = composite.get_observation(var_id, period)
            except MissingDataError:
                return False
            if actual != self.expected[var_id]:
                return False
        return True

    def immutables_pass(self, composite: Composite) -> bool:
        for var_id in self.immutable_vars:
            try:
                actual: Optional[Any] = composite.get_immutable(var_id)
            except MissingDataError:
                return False
            if actual != self.expected[var_id]:
                return False
        return True

    def passes(self, composite: Composite) -> bool:
        if not self.filters:
            return True

        if not self.immutables_pass(composite):
            return False
        for period in composite.periods:
            if self.temporals_pass(composite, period):
                return True
        return False

    def narrow(self, composite: Composite) -> None:
        if not self.narrows:
            return

        if len(self.immutable_vars) > 0 and not self.immutables_pass(composite):
            composite.content = {}

        else:
            for period in composite.periods:
                if not self.temporals_pass(composite, period):
                    del composite.content[period]
