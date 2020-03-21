from abc import ABC, abstractmethod
from typing import Any, cast, Dict

from polytropos.actions.filter._nestable_filter import NestableFilter
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema
from polytropos.util.nesteddicts import MissingDataError, MISSING_VALUE

from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId, Variable, Primitive

from polytropos.actions.filter.univariate.__passes import AllPeriodsCompareTrue, AnyPeriodComparesTrue, \
    EarliestPeriodComparesTrue, LatestPeriodComparesTrue, NoPeriodComparesTrue, UnivariateCompositeTester

TESTERS: Dict = {
    "any": AnyPeriodComparesTrue,
    "all": AllPeriodsCompareTrue,
    "earliest": EarliestPeriodComparesTrue,
    "latest": LatestPeriodComparesTrue,
    "never": NoPeriodComparesTrue
}


class UnivariateFilter(NestableFilter, ABC):
    """A filter that involves checking values against only one variable."""

    def __init__(self, context: Context, schema: Schema, var_id: str, narrows: bool = True, filters: bool = True,
                 pass_condition: str = "any"):

        super().__init__(context, schema, narrows, filters)

        pass_condition = pass_condition.lower()
        if pass_condition not in TESTERS:
            raise ValueError('Unrecognized pass condition "%s." Known pass conditions: %s.' % (pass_condition,
                                                                                               sorted(TESTERS.keys())))
        self.tester: UnivariateCompositeTester = TESTERS[pass_condition](self)

        self.var_id: VariableId = cast(VariableId, var_id)

        variable: Variable = self.schema.get(self.var_id)
        if variable is None:
            raise ValueError('Unrecognized variable ID "%s"' % self.var_id)

        # If narrowing is disabled, the comparison variable should not be immutable
        if self.narrows and not variable.temporal:
            raise ValueError("Narrowing by comparison cannot be performed on an immutable variable.")

        self.variable: Primitive = cast(Primitive, variable)

    def passes_composite(self, composite: Composite) -> bool:
        return self.tester(composite)

    @abstractmethod
    def compares_true(self, value: Any) -> bool:
        pass

    @abstractmethod
    def missing_value_passes(self) -> bool:
        pass

    def compares_case_insensitive(self, value: Any) -> bool:
        if value is MISSING_VALUE:
            return self.missing_value_passes()

        if self.variable.data_type == "Text" and value is not None:
            value = value.lower()
        return self.compares_true(value)

    def narrow(self, composite: Composite) -> None:
        if self.narrows:
            assert self.variable.temporal, "Attempting to narrow on immutable variable despite post-init check"

        super().narrow(composite)

    def passes_period(self, composite: Composite, period: str) -> bool:
        try:
            value: Any = composite.get_observation(self.var_id, period)
        except MissingDataError:
            value = MISSING_VALUE

        return self.compares_case_insensitive(value)
