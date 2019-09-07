from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Deque, List

from polytropos.actions.filter import Filter
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId, Variable
from polytropos.util.nesteddicts import MissingDataError

@dataclass
class HasAllSpecificValues(Filter):
    """AND logic for filtering and narrowing (may be used for either or both).

    Filtering: Includes only records that have ever had a period in which each specified field had the specified
    value. All temporal fields specified must have had the specified value in the same period (temporal variables are
    checked against all periods).

    Narrowing: Includes only periods in which each specified field has the specified value. Immutable values count
    against all periods; i.e., if an immutable value is incorrect, the composite will be emptied.
    """

    expected: Dict[VariableId, Optional[Any]]
    narrows: bool = field(default=True)
    filters: bool = field(default=True)

    def __post_init__(self):
        immutable_vars: Deque[VariableId] = deque()
        temporal_vars: Deque[VariableId] = deque()

        for var_id in self.expected.keys():
            var: Variable = self.schema.get(var_id)
            if var is None:
                raise ValueError('Unrecognized variable ID "%s"' % var_id)
            if var.temporal:
                temporal_vars.append(var_id)
            else:
                immutable_vars.append(var_id)

        self.immutable_vars: List[VariableId] = list(immutable_vars)
        self.temporal_vars: List[VariableId] = list(temporal_vars)

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

        if not self.immutables_pass(composite):
            composite.content = {}

        else:
            for period in composite.periods:
                if not self.temporals_pass(composite, period):
                    del composite.content[period]
