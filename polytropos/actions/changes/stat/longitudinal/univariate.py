from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change
from polytropos.ontology.variable import VariableId, Variable, Primitive, Text

@dataclass  # type: ignore
class LongitudinalUnivariateStatistic(Change, ABC):
    """Calculate a univariate statistic concerning a temporal variable across all periods for a particular composite,
    and assign the statistic to an immutable variable."""
    subject: VariableId
    target: VariableId
    period_id_target: Optional[VariableId] = field(default=None)

    def __post_init__(self) -> None:
        subject_var: Variable = self.schema.get(self.subject)
        if not isinstance(subject_var, Primitive):
            raise ValueError("Longitudinal subject variable must be a Primitive data type.")
        if not subject_var.temporal:
            raise ValueError("Longitudinal subject variable must be temporal.")

        target_var: Variable = self.schema.get(self.target)
        if not isinstance(target_var, Primitive):
            raise ValueError("Longitudinal target variable must be a Primitive data type.")
        if target_var.temporal:
            raise ValueError("Longitudinal target variable must be immutable.")

        if self.period_id_target:
            period_id_target_var: Variable = self.schema.get(self.period_id_target)
            if not isinstance(period_id_target_var, Text):
                raise ValueError("Longitudinal period identifier target must be a Text variable.")
            if period_id_target_var.temporal:
                raise ValueError("Longitudinal period identifier target must be immutable.")

