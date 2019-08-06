from typing import Any, Iterator, Dict

from polytropos.ontology.variable import Variable


class SourceNotFoundException(RuntimeError):
    pass


class DocumentValueProvider:
    def __init__(self, document: Dict):
        self.document = document

    def variable_value(self, variable: Variable, parent_id_to_stop: str = "") -> Any:
        """Function that finds a variable (given its id) in a document. The
        parent_id_to_stop parameter is used to limit the depth for the recursive search"""
        # TODO What type is parent supposed to be here? Play around to find out.
        if len(self.document) == 0:
            raise SourceNotFoundException

        ancestors = variable.ancestors(parent_id_to_stop)
        path = reversed([var.name for var in ancestors])
        try:
            return self.value(path)
        except KeyError:
            raise SourceNotFoundException

    def value(self, path: Iterator[str]) -> Any:
        result = self.document
        for name in path:
            result = result[name]
        return result
