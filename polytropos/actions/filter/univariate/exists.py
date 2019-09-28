from abc import ABC
from typing import Optional, Any

from polytropos.actions.filter.univariate.__univariate import UnivariateFilter
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

class Exists(UnivariateFilter):
    """Requires that a variable have a non-trivial value in order to pass. For primitives, that means non-null; for
    Folders, Lists, or NamedLists, that means non-empty."""

    def missing_value_passes(self) -> bool:
        return False

    def compares_true(self, value: Any) -> bool:
        return not trivial(value)

class DoesNotExist(UnivariateFilter):
    """Requires that a variable either be absent or have a trivial value in at least one period in order to pass."""

    def missing_value_passes(self) -> bool:
        return True

    def compares_true(self, value: Any) -> bool:
        return trivial(value)
