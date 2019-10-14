from typing import Optional, Any

from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.ontology.variable import Variable, VariableId, Container


class TraceDocumentValueProvider(DocumentValueProvider):
    def variable_value(self, variable: Variable, parent_id_to_stop: Optional[VariableId] = None) -> Any:
        value = super().variable_value(variable, parent_id_to_stop)
        if isinstance(variable, Container):
            return value
        return variable.var_id
