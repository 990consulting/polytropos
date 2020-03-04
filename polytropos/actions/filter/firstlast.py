from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Set, List

from polytropos.ontology.composite import Composite

from polytropos.actions.filter import Filter

@dataclass
class FirstLastFilter(Filter):
    reverse: bool
    n_periods: int = field(default=1)

    def get_retained(self, periods: Set[str]) -> Set:
        periods_ranked: List[str] = sorted(periods, reverse=self.reverse)

        ret: Set = set()
        for i, period in enumerate(periods_ranked):
            if i >= self.n_periods:
                break
            ret.add(period)

        return ret

    def narrow(self, composite: Composite) -> None:
        periods: Set = set(composite.periods)
        if len(periods) == 0:
            return

        to_retain: Set[str] = self.get_retained(periods)
        to_remove: Set[str] = set(periods) - to_retain
        for period in to_remove:
            del composite.content[period]

@dataclass
class LatestFilter(FirstLastFilter):
    """Filters out all temporal periods except the latest period."""
    reverse: bool = field(default=True, init=False)

@dataclass
class EarliestFilter(FirstLastFilter):
    """Filters out all temporal periods except the earliest period."""
    reverse: bool = field(default=False, init=False)
