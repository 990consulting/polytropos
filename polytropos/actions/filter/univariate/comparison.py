from abc import ABC
from typing import Any, cast

from polytropos.actions.filter.univariate.__univariate import UnivariateFilter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

class ComparisonFilter(UnivariateFilter, ABC):
    def __init__(self, context: Context, schema: Schema, var_id: str, threshold: str, narrows: bool=True,
                 filters: bool=True):

        super(ComparisonFilter, self).__init__(context, schema, var_id, narrows=narrows, filters=filters)
        if threshold is None:
            raise ValueError('Must specify threshold value for comparison filters.')

        self.threshold = self.variable.cast(threshold)

        if self.variable.data_type == "Text":
            t: str = cast(str, self.threshold).lower()
            self.threshold = t

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
