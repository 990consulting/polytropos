from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, Tuple
from polytropos.actions.changes.stat.cross_sectional.univariate import CrossSectionalUnivariateStatistic
from polytropos.tools.qc import POLYTROPOS_NA
from polytropos.ontology.composite import Composite

class _CrossSectionalMinMax(CrossSectionalUnivariateStatistic, ABC):

    @abstractmethod
    def _cmp(self, argument: Any, limit: Any) -> bool:
        pass

    def _sets_new_limit(self, argument: Optional[Any], limit: Optional[Any]) -> bool:
        if argument is None:
            return False

        if limit is None:
            return True

        return self._cmp(argument, limit)

    def _handle(self, content: Dict) -> Tuple[Optional[Any], Optional[str]]:
        limit: Optional[Any] = None
        arg_limit: Optional[str] = POLYTROPOS_NA
        for value, identifier in self.iterate_over(content):
            if self._sets_new_limit(value, limit):
                limit = value
                arg_limit = identifier
        return limit, arg_limit

    def __call__(self, composite: Composite) -> None:
        if self.temporal:
            for period in composite.periods:
                content: Dict = composite.content[period]
                limit, arg_limit = self._handle(content)
                self._assign(content, limit, arg_limit)
        else:
            content = composite.content["immutable"]
            limit, arg_limit = self._handle(content)
            self._assign(content, limit, arg_limit)

class CrossSectionalMinimum(_CrossSectionalMinMax):  # type: ignore
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument < limit

class CrossSectionalMaximum(_CrossSectionalMinMax):  # type: ignore
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument > limit
