from dataclasses import dataclass, field
from typing import Optional

from polytropos.actions.changes.available_v2 import BestAvailableV2
from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId


@dataclass  # type: ignore
class BestAvailable(Change):
    """Used for consolidating multiple values into an immutable, "preferred" value. If an immutable source is specified
    and it exists, this is used. Otherwise, the newest nontrivial value for the temporal source is used."""

    temporal_source: VariableId
    target: VariableId
    immutable_source: Optional[VariableId] = field(default=None)
    use_older_periods: bool = field(default=True)
    bestAvailableV2: BestAvailableV2 = field(init=False)

    def __post_init__(self) -> None:
        sources = []
        if self.immutable_source is not None:
            sources.append(self.immutable_source)
        sources.append(self.temporal_source)
        self.bestAvailableV2 = BestAvailableV2(self.schema, self.lookups, self.target, sources, not self.use_older_periods)

    def __call__(self, composite: Composite) -> None:
        self.bestAvailableV2(composite)
