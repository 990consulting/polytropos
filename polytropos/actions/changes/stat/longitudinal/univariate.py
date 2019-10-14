from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from polytropos.tools.qc import POLYTROPOS_NA

from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change
from polytropos.ontology.variable import VariableId, Variable, Primitive, Text
from polytropos.util.nesteddicts import MissingDataError

@dataclass  # type: ignore
class LongitudinalUnivariateStatistic(Change, ABC):
    """Calculate a univariate statistic concerning a temporal variable across all periods for a particular composite,
    and assign the statistic to an immutable variable."""
    subject: VariableId
    target: VariableId
    period_id_target: Optional[VariableId] = field(default=None)

    def __post_init__(self) -> None:
        subject_var: Variable = self.schema.get(self.subject)
        if not isinstance(subject_var, Primitive):
            raise ValueError("Longitudinal subject variable must be a Primitive data type.")
        if not subject_var.temporal:
            raise ValueError("Longitudinal subject variable must be temporal.")

        target_var: Variable = self.schema.get(self.target)
        if not isinstance(target_var, Primitive):
            raise ValueError("Longitudinal target variable must be a Primitive data type.")
        if target_var.temporal:
            raise ValueError("Longitudinal target variable must be immutable.")

        if self.period_id_target:
            period_id_target_var: Variable = self.schema.get(self.period_id_target)
            if not isinstance(period_id_target_var, Text):
                raise ValueError("Longitudinal period identifier target must be a Text variable.")
            if period_id_target_var.temporal:
                raise ValueError("Longitudinal period identifier target must be immutable.")

class _LongitudinalMinMax(LongitudinalUnivariateStatistic, ABC):
    @abstractmethod
    def _cmp(self, argument: Any, limit: Any) -> bool:
        pass

    def _sets_new_limit(self, argument: Optional[Any], limit: Optional[Any]) -> bool:
        if argument is None:
            return False

        if limit is None:
            return True

        return self._cmp(argument, limit)

    def __call__(self, composite: Composite) -> None:
        limit: Optional[Any] = None
        limit_period: Optional[str] = POLYTROPOS_NA

        for period in composite.periods:
            try:
                value: Optional[Any] = composite.get_observation(self.subject, period)
                if value is not None and self._sets_new_limit(value, limit):
                    limit = value
                    limit_period = period
            except MissingDataError:
                continue

        if limit is not None:
            composite.put_immutable(self.target, limit)
            if self.period_id_target is not None:
                assert limit_period != POLYTROPOS_NA, "Non-null minimum or maximum found, yet no period identified?"
                composite.put_immutable(self.period_id_target, limit_period)

class LongitudinalMinimum(_LongitudinalMinMax):
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument < limit

class LongitudinalMaximum(_LongitudinalMinMax):
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument > limit
