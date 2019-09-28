from abc import ABC
from typing import Optional, Any

from polytropos.util.nesteddicts import MissingDataError

from polytropos.ontology.composite import Composite

from polytropos.actions.filter import Filter
from polytropos.ontology.variable import VariableId, Variable
from dataclasses import dataclass, field

def trivial(value: Optional[Any]) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, dict)):
        if len(value) == 0:
            return True
    return False

@dataclass
class ExistenceFilter(Filter, ABC):
    var_id: VariableId
    narrows: bool = field(default=True)
    filters: bool = field(default=True)

    def __post_init__(self) -> None:
        self.var: Variable = self.schema.get(self.var_id)
        if self.var is None:
            raise ValueError('Unrecognized variable ID "%s"' % self.var_id)
        if self.narrows and not self.var.temporal:
            raise ValueError("Exists filter cannot narrow on immutable variable %s." % self.var_id)

class Exists(ExistenceFilter):
    """Requires that a variable have a non-trivial value in order to pass. For primitives, that means non-null; for
    Folders, Lists, or NamedLists, that means non-empty."""

    def narrow(self, composite: Composite) -> None:
        if not self.narrows:
            return

        for period in composite.periods:
            try:
                value: Optional[Any] = composite.get_observation(self.var_id, period)
            except MissingDataError:
                del composite.content[period]
                continue
            if trivial(value):
                del composite.content[period]
                continue

    def passes(self, composite: Composite) -> bool:
        if not self.filters:
            return True

        if not self.var.temporal:
            try:
                value: Optional[Any] = composite.get_immutable(self.var_id)
            except MissingDataError:
                return False
            return not trivial(value)

        for period in composite.periods:
            try:
                value = composite.get_observation(self.var_id, period)
            except MissingDataError:
                continue
            if not trivial(value):
                return True

        return False

class DoesNotExist(ExistenceFilter):
    """Requires that a variable either be absent or have a trivial value in at least one period in order to pass."""

    def narrow(self, composite: Composite) -> None:
        if not self.narrows:
            return

        for period in composite.periods:
            try:
                value: Optional[Any] = composite.get_observation(self.var_id, period)
            except MissingDataError:
                continue
            if not trivial(value):
                del composite.content[period]

    def passes(self, composite: Composite) -> bool:
        if not self.filters:
            return True

        if not self.var.temporal:
            try:
                value: Optional[Any] = composite.get_immutable(self.var_id)
            except MissingDataError:
                return True
            return trivial(value)

        if len(list(composite.periods)) == 0:
            return True

        for period in composite.periods:
            try:
                value = composite.get_observation(self.var_id, period)
            except MissingDataError:
                return True
            if trivial(value):
                return True

        return False
