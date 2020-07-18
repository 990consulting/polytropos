from typing import Optional, Any

from polytropos.ontology.variable import Variable
from polytropos.util.nesteddicts import MissingDataError

from polytropos.ontology.composite import Composite

from polytropos.actions.changes.stat.longitudinal.univariate import LongitudinalUnivariateStatistic

class LongitudinalMean(LongitudinalUnivariateStatistic):
    def __post_init__(self) -> None:
        super(LongitudinalMean, self).__post_init__()
        if self.period_id_target is not None:
            raise ValueError("Unexpected parameter 'period_id_target' in LongitudinalMean")

        subject_var: Variable = self.schema.get(self.subject)
        if subject_var.data_type not in {"Currency", "Decimal", "Integer"}:
            raise ValueError("LongitudinalMean requires a numeric subject")

        target_var: Variable = self.schema.get(self.target)
        if target_var.data_type not in {"Currency", "Decimal", "Integer"}:
            raise ValueError("LongitudinalMean requires a numeric target")

    def __call__(self, composite: Composite) -> None:
        total: float = 0.0
        n: int = 0
        for period in composite.periods:
            try:
                value: Optional[Any] = composite.get_observation(self.subject, period)
                if value is not None:
                    total += float(value)
                    n += 1
            except MissingDataError:
                continue

        if n == 0:
            composite.put_immutable(self.target, None)
        else:
            avg: float = total / n
            composite.put_immutable(self.target, avg)