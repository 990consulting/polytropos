from abc import ABC, abstractmethod

from polytropos.actions.filter import Filter
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema


class NestableFilter(Filter, ABC):
    """Base class for filters that could be nested into NestedFilter"""

    def __init__(self, context: Context, schema: Schema, narrows: bool = True, filters: bool = True):
        super().__init__(context, schema)
        self.narrows: bool = narrows
        self.filters: bool = filters

    @abstractmethod
    def passes_composite(self, composite: Composite) -> bool:
        """Evaluate whether the entire Composite should be included at the next Step or not."""
        pass

    @abstractmethod
    def passes_period(self, composite: Composite, period: str) -> bool:
        """Evaluate whether the Composite period should be included at the next Step or not."""
        pass

    def passes(self, composite: Composite) -> bool:
        if not self.filters:
            return True
        return self.passes_composite(composite)

    def narrow(self, composite: Composite) -> None:
        if not self.narrows:
            return

        for period in composite.periods:
            if not self.passes_period(composite, period):
                del composite.content[period]
