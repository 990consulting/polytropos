from typing import Iterable, Tuple, Any, Dict, List, Optional
from collections import Counter

from polytropos.util.nesteddicts import MissingDataError

from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.context import Context
from polytropos.actions.scan import Scan
from polytropos.ontology.variable import VariableId

def value_to_rank(observations: Counter) -> Dict[Any, int]:
    rank: Dict = {}
    distinct_values: List[Any] = sorted(observations.keys(), reverse=True)
    offset: int = 0
    for value in distinct_values:
        offset += observations[value]
        rank[value] = offset
    return rank

class Rank(Scan):
    """Similar to Quantile, Rank provides an ordering of non-temporal, integer values across the set of composites. This
    particular ranking puts the highest value at 1, and resolves ties by assigning the lowest possible value. For
    example, given the values [45, 7, 7, 0], the ranking would be 45->1, 7->3, 0->4."""
    def __init__(self, context: Context, schema: Schema, source: VariableId, target: VariableId):
        super(Rank, self).__init__(context, schema)
        self.source: VariableId = source
        self.target: VariableId = target

        source_var = self.schema.get(self.source)
        target_var = self.schema.get(self.target)

        if source_var.temporal or target_var.temporal:
            raise ValueError("Rank scan compares entities and thus only works on immutable variables.")

        assert source_var.data_type in {"Integer", "Currency", "Decimal"}, "Rank requires a numeric argument"
        assert target_var.data_type == "Integer", "Rank target must be an Integer"

        self.ranks: Dict[Any, int] = {}

    def extract(self, composite: Composite) -> Any:
        return composite.get_immutable(self.source, treat_missing_as_null=True)

    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        observations: Counter = Counter()
        for composite_id, obs in extracts:  # types: str, Optional[int]
            if obs is None:
                continue
            observations[obs] += 1

        if len(observations) == 0:
            return

        self.ranks = value_to_rank(observations)

    def alter(self, composite_id: str, composite: Composite) -> None:
        try:
            value: Any = composite.get_immutable(self.source)
        except MissingDataError:
            return
        assert value in self.ranks, "Value {} did not get recorded in value-to-rank map".format(value)
        rank: int = self.ranks[value]
        composite.put_immutable(self.target, rank)