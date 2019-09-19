from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, cast

from polytropos.util.nesteddicts import MissingDataError

from polytropos.actions.filter import Filter
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId, Variable, Primitive

@dataclass
class ComparisonFilter(Filter, ABC):  # type: ignore
    var_id: VariableId
    threshold: Any
    narrows: bool = field(default=True)
    filters: bool = field(default=True)

    def __post_init__(self) -> None:
        self.variable: Variable = self.schema.get(self.var_id)
        if self.variable is None:
            raise ValueError('Unrecognized variable ID "%s"' % self.var_id)
        if not isinstance(self.variable, Primitive):
            raise ValueError('Non-primitive data type %s cannot be compared' % self.variable.data_type)
        if self.threshold is None:
            raise ValueError('Must specify threshold value for comparison filters.')

        # If narrowing is disabled, the comparison variable should not be immutable
        if self.narrows and not self.variable.temporal:
            raise ValueError("Narrowing by comparison cannot be performed on an immutable variable.")

        self.variable = cast(Primitive, self.variable)
        self.threshold = self.variable.cast(self.threshold)

        if self.variable.data_type == "Text":
            self.threshold = self.threshold.lower()

    @abstractmethod
    def compares_true(self, value: Any) -> bool:
        pass

    def compares_case_insensitive(self, value: Any) -> bool:
        if self.variable.data_type == "Text":
            value = value.lower()
        return self.compares_true(value)

    def narrow(self, composite: Composite) -> None:
        if not self.narrows:
            return
        assert self.variable.temporal, "Attempting to narrow on immutable variable despite post-init check"

        for period in composite.periods:
            try:
                value: Any = composite.get_observation(self.var_id, period)
            except MissingDataError:
                del composite.content[period]
                continue
            if not self.compares_case_insensitive(value):
                del composite.content[period]

    def passes(self, composite: Composite) -> bool:
        if not self.filters:
            return True

        if not self.variable.temporal:
            try:
                value: Any = composite.get_immutable(self.var_id)
            except MissingDataError:
                return False
            return self.compares_case_insensitive(value)

        for period in composite.periods:
            try:
                value = composite.get_observation(self.var_id, period)
            except MissingDataError:
                continue
            if self.compares_case_insensitive(value):
                return True

        return False

class AtLeast(ComparisonFilter):
    def compares_true(self, value: Any) -> bool:
        return value >= self.threshold

class AtMost(ComparisonFilter):
    def compares_true(self, value: Any) -> bool:
        return value <= self.threshold

class GreaterThan(ComparisonFilter):
    def compares_true(self, value: Any) -> bool:
        return value > self.threshold

class LessThan(ComparisonFilter):
    def compares_true(self, value: Any) -> bool:
        return value < self.threshold

class NotEqualTo(ComparisonFilter):
    def compares_true(self, value: Any) -> bool:
        return value != self.threshold

class EqualTo(ComparisonFilter):
    def compares_true(self, value: Any) -> bool:
        return value == self.threshold
