from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Deque, List

from polytropos.actions.filter import Filter
from polytropos.ontology.variable import VariableId, Variable

@dataclass
class SpecificValuesFilter(Filter):
    expected: Dict[VariableId, Optional[Any]]
    narrows: bool = field(default=True)
    filters: bool = field(default=True)

    def __post_init__(self) -> None:
        immutable_vars: Deque[VariableId] = deque()
        temporal_vars: Deque[VariableId] = deque()

        for var_id in self.expected.keys():
            var: Variable = self.schema.get(var_id)
            if var is None:
                raise ValueError('Unrecognized variable ID "%s"' % var_id)
            if var.temporal:
                temporal_vars.append(var_id)
            else:
                immutable_vars.append(var_id)

        self.immutable_vars: List[VariableId] = list(immutable_vars)
        self.temporal_vars: List[VariableId] = list(temporal_vars)
