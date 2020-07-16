from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any, Dict

from polytropos.actions.changes.stat.cross_sectional.univariate import CrossSectionalUnivariateStatistic
from polytropos.ontology.composite import Composite

class CrossSectionalReduce(CrossSectionalUnivariateStatistic, ABC):
    @abstractmethod
    def _handle(self, content: Dict) -> Any:
        pass

    def __call__(self, composite: Composite) -> None:
        if self.temporal:
            for period in composite.periods:
                t_content: Dict = composite.content[period]
                value: Any = self._handle(t_content)
                self._assign(t_content, value)
        else:
            i_content: Optional[Dict] = composite.content.get("immutable")
            if i_content is None:
                return
            value: Any = self._handle(i_content)
            self._assign(i_content, value)

class CrossSectionalCount(CrossSectionalReduce):
    def _handle(self, content: Dict) -> int:
        count: int = 0
        for value, _ in self.iterate_over(content):
            if value is not None:
                count += 1
        return count

class CrossSectionalMean(CrossSectionalReduce):
    def _handle(self, content: Dict) -> None:
        assert False, "Not yet implemented!"

class CrossSectionalMedian(CrossSectionalReduce):
    def _handle(self, content: Dict) -> None:
        assert False, "Not yet implemented!"

