from dataclasses import dataclass, field
from typing import Iterable, Tuple, Any, Optional, Dict, Iterator, List
from collections import Counter

from polytropos.actions.scan import Scan
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId

def val2qtile(observations: Counter) -> Dict[int, float]:
    distinct_values: List[int] = sorted(observations.keys())
    n_obs: int = sum(observations.values())
    ret: Dict = {}
    offset: int = 0
    for value in distinct_values:
        qtile: float = offset / n_obs
        ret[value] = qtile
        offset += observations[value]
    return ret

@dataclass
class Quantile(Scan):
    """Extracts an numeric value from each composite, assigning a quantile score to each unique value. For each
    observation with a non-null source value, store the associated quantile in the target variable."""

    source: VariableId
    target: VariableId
    value_to_quantile: Dict[int, float] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        source_var = self.schema.get(self.source)
        target_var = self.schema.get(self.target)

        if source_var.temporal or target_var.temporal:
            raise ValueError("Quantile scan compares entities and thus only works on immutable variables.")

        assert source_var.data_type in {"Integer", "Currency"}, "Quantile currently only implemented for integers"
        assert target_var.data_type == "Decimal", "Quantile target must be a Decimal"

    def extract(self, composite: Composite) -> Optional[int]:
        return composite.get_immutable(self.source, treat_missing_as_null=True)

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        observations: Counter = Counter()
        for composite_id, obs in extracts:  # types: str, Optional[int]
            if obs is None:
                continue
            int_obs: int = int(obs)
            observations[int_obs] += 1

        if len(observations) == 0:
            return

        self.value_to_quantile = val2qtile(observations)

    def alter(self, composite_id: str, composite: Composite) -> None:
        value: Optional[int] = composite.get_immutable(self.source, treat_missing_as_null=True)
        if value is None:
            return
        assert value in self.value_to_quantile, "Value {} did not get recorded in value-to-quantile map".format(value)
        quantile: float = self.value_to_quantile[value]
        composite.put_immutable(self.target, quantile)

