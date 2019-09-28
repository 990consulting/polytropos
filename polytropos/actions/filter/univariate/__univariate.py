from abc import ABC, abstractmethod
from typing import Any, cast, List, Dict, Type, Callable

from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema
from polytropos.util.nesteddicts import MissingDataError, MISSING_VALUE

from polytropos.actions.filter import Filter
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId, Variable, Primitive

from polytropos.actions.filter.univariate.__passes import AllPeriodsCompareTrue, AnyPeriodComparesTrue, \
    EarliestPeriodComparesTrue, LatestPeriodComparesTrue, NoPeriodComparesTrue

TESTERS: Dict = {
    "any": AnyPeriodComparesTrue,
    "all": AllPeriodsCompareTrue,
    "earliest": EarliestPeriodComparesTrue,
    "latest": LatestPeriodComparesTrue,
    "never": NoPeriodComparesTrue
}

class UnivariateFilter(Filter, ABC):
    """A filter that involves checking values against only one variable."""

    def __init__(self, context: Context, schema: Schema, var_id: str, narrows: bool=True, filters: bool=True,
                 pass_condition: str="any"):

        super(UnivariateFilter, self).__init__(context, schema)

        pass_condition = pass_condition.lower()
        if pass_condition not in TESTERS:
            raise ValueError('Unrecognized pass condition "%s." Known pass conditions: %s.' % (pass_condition,
                                                                                               sorted(TESTERS.keys())))
        self.passes: Callable = TESTERS[pass_condition](self)  # type: ignore

        self.var_id: VariableId = cast(VariableId, var_id)
        self.narrows: bool = narrows
        self.filters: bool = filters

        variable: Variable = self.schema.get(self.var_id)
        if variable is None:
            raise ValueError('Unrecognized variable ID "%s"' % self.var_id)

        # If narrowing is disabled, the comparison variable should not be immutable
        if self.narrows and not variable.temporal:
            raise ValueError("Narrowing by comparison cannot be performed on an immutable variable.")

        self.variable: Primitive = cast(Primitive, variable)

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
        if not self.narrows:
            return
        assert self.variable.temporal, "Attempting to narrow on immutable variable despite post-init check"

        for period in composite.periods:
            try:
                value: Any = composite.get_observation(self.var_id, period)
            except MissingDataError:
                value = MISSING_VALUE

            if not self.compares_case_insensitive(value):
                del composite.content[period]
