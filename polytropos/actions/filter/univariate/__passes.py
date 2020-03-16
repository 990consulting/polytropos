from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import TYPE_CHECKING, Any, List

from polytropos.ontology.composite import Composite
from polytropos.util.nesteddicts import MissingDataError, MISSING_VALUE

if TYPE_CHECKING:
    from polytropos.actions.filter.univariate.__univariate import UnivariateFilter

@dataclass  # type: ignore
class UnivariateCompositeTester(ABC):
    """Tests whether a Composite should be passed by a UnivariateFilter. The behavior is always the same for immutable
    variables: the Composite passes if and only if the immutable variable passes the filter criterion."""

    parent: "UnivariateFilter"

    @abstractmethod
    def passes_temporal(self, composite: Composite) -> bool:
        pass

    def __call__(self, composite: Composite) -> bool:
        if not self.parent.variable.temporal:
            try:
                value: Any = composite.get_immutable(self.parent.var_id)
            except MissingDataError:
                value = MISSING_VALUE
            return self.parent.compares_case_insensitive(value)

        return self.passes_temporal(composite)

class AllPeriodsCompareTrue(UnivariateCompositeTester):
    """If the variable is temporal, require that the value of the filter variable compares true for every period. If
    there are no periods, the value depends on the class' missing_value_passes method."""

    def passes_temporal(self, composite: Composite) -> bool:
        periods: List = list(composite.periods)
        if len(periods) == 0 and not self.parent.missing_value_passes():
            return False

        for period in periods:
            try:
                value = composite.get_observation(self.parent.var_id, period)
            except MissingDataError:
                value = MISSING_VALUE
            if not self.parent.compares_case_insensitive(value):
                return False

        return True

class AnyPeriodComparesTrue(UnivariateCompositeTester):
    """If the variable is temporal, require that the value of the filter variable compares true for at least one
    period. If there are no periods, the value depends on the class' missing_value_passes method."""

    def passes_temporal(self, composite: Composite) -> bool:
        periods: List = list(composite.periods)
        if len(periods) == 0 and self.parent.missing_value_passes():
            return True

        for period in periods:
            try:
                value = composite.get_observation(self.parent.var_id, period)
            except MissingDataError:
                value = MISSING_VALUE
            if self.parent.compares_case_insensitive(value):
                return True

        return False

class EarliestPeriodComparesTrue(UnivariateCompositeTester):
    """If the variable is temporal, require that the value of the filter variable compares true for the earliest
    period. If there are no periods, the value depends on the class' missing_value_passes method."""

    def passes_temporal(self, composite: Composite) -> bool:
        periods: List = list(composite.periods)
        if len(periods) == 0:
            return self.parent.missing_value_passes()

        earliest: str = min(periods)
        try:
            value = composite.get_observation(self.parent.var_id, earliest)
        except MissingDataError:
            value = MISSING_VALUE
        return self.parent.compares_case_insensitive(value)

class LatestPeriodComparesTrue(UnivariateCompositeTester):
    """If the variable is temporal, require that the value of the filter variable compares true for the latest
    period. If there are no periods, the value depends on the class' missing_value_passes method."""

    def passes_temporal(self, composite: Composite) -> bool:
        periods: List = list(composite.periods)
        if len(periods) == 0:
            return self.parent.missing_value_passes()

        latest: str = max(periods)
        try:
            value = composite.get_observation(self.parent.var_id, latest)
        except MissingDataError:
            value = MISSING_VALUE
        return self.parent.compares_case_insensitive(value)

class NoPeriodComparesTrue(UnivariateCompositeTester):
    """If the variable is temporal, require that no period has a value that compares true. If there are no periods, the
    composite passes."""

    def passes_temporal(self, composite: Composite) -> bool:
        periods: List = list(composite.periods)
        if len(periods) == 0:
            return True

        for period in periods:
            try:
                value = composite.get_observation(self.parent.var_id, period)
            except MissingDataError:
                value = MISSING_VALUE
            if self.parent.compares_case_insensitive(value):
                return False

        return True
