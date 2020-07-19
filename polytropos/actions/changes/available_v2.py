from dataclasses import dataclass, field
from typing import Optional, Any, List, Set

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import TrackType
from polytropos.ontology.variable import VariableId, Variable
from polytropos.util.nesteddicts import MissingDataError


@dataclass  # type: ignore
class BestAvailableV2(Change):
    """Used for consolidating multiple values into an immutable, "preferred" value."""

    target: VariableId
    sources: List[VariableId]
    use_only_current: bool = field(default=False)
    temporal_sources: Set[VariableId] = field(init=False, default_factory=set)

    def __post_init__(self) -> None:
        target_var: Optional[Variable] = self.schema.get(self.target, track_type=TrackType.IMMUTABLE)
        if target_var is None:
            raise ValueError('Unknown target variable "%s"' % self.target)

        for source_var_id in self.sources:
            source_var: Optional[Variable] = self.schema.get(source_var_id)
            if source_var is None:
                raise ValueError('Unknown source variable "%s"' % source_var_id)

            if source_var.data_type != target_var.data_type:
                raise ValueError('Source variable id "%s" has data type "%s", but target variable id "%s" has data type "%s"' %
                                 (source_var_id, source_var.data_type, self.target, target_var.data_type))

            if self.schema.is_temporal(source_var_id):
                self.temporal_sources.add(source_var_id)

    def __call__(self, composite: Composite) -> None:
        periods_to_consider: List[str] = []
        if len(self.temporal_sources) > 0:
            periods_to_consider = sorted(composite.periods, reverse=True)
            if self.use_only_current and len(periods_to_consider) > 0:
                periods_to_consider = [periods_to_consider[0]]

        for source_var_id in self.sources:
            value: Any
            if source_var_id in self.temporal_sources:
                value = self._get_temporal_value(composite, source_var_id, periods_to_consider)
            else:
                value = self._get_immutable_value(composite, source_var_id)

            if value is not None:
                composite.put_immutable(self.target, value)
                return

    def _get_temporal_value(self, composite: Composite, source_var_id: VariableId, periods: List[str]) -> Any:
        for period in periods:
            try:
                value = composite.get_observation(source_var_id, period)
                if value is not None:
                    return value
            except MissingDataError:
                continue

        return None

    def _get_immutable_value(self, composite: Composite, source_var_id: VariableId) -> Any:
        try:
            value = composite.get_immutable(source_var_id)
            if value is not None:
                return value
        except MissingDataError:
            pass

        return None
