from collections import OrderedDict
from typing import List as ListType, Any, Dict
import logging

from polytropos.actions.translate.type_translators.__base import BaseTypeTranslator
from polytropos.actions.translate.type_translators.__decorator import type_translator
from polytropos.ontology.variable import VariableId, List


@type_translator(List)
class ListTranslator(BaseTypeTranslator[ListType[Dict[str, Any]], ListType["OrderedDict[str, Any]"]]):
    """Translate for lists"""

    def initial_result(self) -> ListType["OrderedDict[str, Any]"]:
        return []

    def initialize(self) -> None:
        self.has_result = True

    def process_source_value(self, source_value: ListType[Dict[str, Any]], source_id: VariableId) -> None:
        # The resulting list is the concatenation of all the translations,
        # source by source

        if source_value is None:
            logging.debug("Encountered null list element in variable %s", source_id)
            return
        # sometimes lists with one element are represented as folders
        if isinstance(source_value, dict):
            source_value = [source_value]
        for item in source_value:  # type: Dict[str, Any]
            # translate the values in the list one by one and add them to
            # the result
            # noinspection PyTypeChecker
            translated: OrderedDict[str, Any] = self.translator.translate(self.composite_id, self.period, item, self.variable.var_id, source_id)
            self.result.append(translated)
