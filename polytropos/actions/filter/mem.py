from dataclasses import dataclass
from typing import List, Iterable, Iterator, Optional

from polytropos.actions.filter import Filter
from polytropos.ontology.composite import Composite
from copy import copy

@dataclass
class InMemoryFilterIterator:
    filters: List[Filter]

    def apply_all(self, composite: Composite) -> Optional[Composite]:
        target: Composite = copy(composite)
        for f in self.filters:
            if not f.passes(target):
                return None
            f.narrow(target)
        return target

    def __call__(self, composites: Iterable[Composite]) -> Iterator[Composite]:
        for composite in composites:
            result: Optional[Composite] = self.apply_all(composite)
            if result is not None:
                yield result
