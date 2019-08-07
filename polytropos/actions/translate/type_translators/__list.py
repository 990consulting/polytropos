from typing import List, Any

from polytropos.actions.translate.type_translators.__base import BaseTypeTranslator
from polytropos.ontology.variable import VariableId


class ListTranslator(BaseTypeTranslator[List[Any]]):
    """Translate for lists"""

    def initial_result(self) -> List[Any]:
        return []

    def initialize(self) -> None:
        self.has_result = True

    def process_source_value(self, source_value: List[Any], source_id: VariableId) -> None:
        # The resulting list is the concatenation of all the translations,
        # source by source

        if source_value is None:
            raise RuntimeError("I don't think this should be possible, because SourceNotFoundException replaced it")
        # sometimes lists with one element are represented as folders
        if isinstance(source_value, dict):
            source_value = [source_value]
        for item in source_value:
            # translate the values in the list one by one and add them to
            # the result
            # noinspection PyTypeChecker
            matches = self.translator(item, self.variable.var_id, source_id)
            self.result.append(matches)
