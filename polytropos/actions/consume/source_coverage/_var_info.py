import sys
from typing import NamedTuple, cast

from polytropos.ontology.variable import VariableId


class VarInfo(NamedTuple):
    """Represents a pair of source/target variable identifiers."""

    source_var_id: VariableId
    target_var_id: VariableId

    def interned(self) -> "VarInfo":
        """Returns a copy with interned fields to reduce memory usage for duplicated identifiers."""

        return VarInfo(
            source_var_id=cast(VariableId, sys.intern(self.source_var_id)),
            target_var_id=cast(VariableId, sys.intern(self.target_var_id)),
        )
