from typing import Any, Dict, Optional, Iterable

from polytropos.ontology.variable import Variable, VariableId


class SourceNotFoundException(RuntimeError):
    pass


class DocumentValueProvider:
    def __init__(self, document: Dict[str, Any]):
        self.document: Dict[str, Any] = document

    def variable_value(self, variable: Variable, parent_id_to_stop: Optional[VariableId] = None) -> Any:
        """Function that finds a variable in a document.
        The parent_id_to_stop parameter is used to limit the depth for the recursive search"""
        # TODO What type is parent supposed to be here? Play around to find out.
        if len(self.document) == 0:
            raise SourceNotFoundException

        ancestors: Iterable[Variable] = variable.ancestors(parent_id_to_stop)
        path: Iterable[str] = reversed([var.name for var in ancestors])
        try:
            return self.value(path)
        except KeyError:
            raise SourceNotFoundException

    def value(self, path: Iterable[str]) -> Any:
        result: Any = self.document
        for name in path:  # type: str
            if not isinstance(result, dict):
                raise KeyError
            result = result[name]
        return result
