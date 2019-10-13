from dataclasses import dataclass, field
from typing import Optional, Any

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId
from polytropos.util.nesteddicts import MissingDataError

@dataclass  # type: ignore
class BestAvailable(Change):
    """Used for consolidating multiple values into an immutable, "preferred" value. If an immutable source is specified
    and it exists, this is used. Otherwise, the newest nontrivial value for the temporal source is used."""

    temporal_source: VariableId
    target: VariableId
    immutable_source: Optional[VariableId] = field(default=None)

    def __call__(self, composite: Composite) -> None:
        if self.immutable_source is not None:
            try:
                value: Optional[Any] = composite.get_immutable(self.immutable_source)
                if value is not None:
                    composite.put_immutable(self.target, value)
                    return
            except MissingDataError:
                pass

        for period in sorted(composite.periods, reverse=True):
            try:
                value = composite.get_observation(self.temporal_source, period)
                if value is not None:
                    composite.put_immutable(self.target, value)
                    return
            except MissingDataError:
                continue
