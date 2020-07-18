from abc import ABC, abstractmethod
from typing import Optional, Any

from polytropos.tools.qc import POLYTROPOS_NA

from polytropos.ontology.composite import Composite

from polytropos.util.nesteddicts import MissingDataError
from polytropos.actions.changes.stat.longitudinal.univariate import LongitudinalUnivariateStatistic

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
