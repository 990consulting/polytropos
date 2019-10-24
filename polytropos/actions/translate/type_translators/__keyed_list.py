from collections import OrderedDict
from typing import Dict, Any

from polytropos.actions.translate.type_translators.__base import BaseTypeTranslator
from polytropos.actions.translate.type_translators.__decorator import type_translator
from polytropos.ontology.variable import VariableId, KeyedList


@type_translator(KeyedList)
class KeyedListTranslator(BaseTypeTranslator[Dict[str, Dict[str, Any]], "OrderedDict[str, OrderedDict[str, Any]]"]):
    """Translate function for keyed lists (similar to python dicts), the
    logic is almost the same as for lists but taking care of the keys.
    Raises ValueError on duplicate keys"""

    def initial_result(self) -> "OrderedDict[str, OrderedDict[str, Any]]":
        return OrderedDict()

    def initialize(self) -> None:
        self.has_result = True

    def process_source_value(self, source_value: Dict[str, Dict[str, Any]], source_id: VariableId) -> None:
        if source_value is None:
            raise RuntimeError("I don't think this should be possible, because SourceNotFoundException replaced it")

        for key, item in source_value.items():  # type: str, Dict[str, Any]
            if key in self.result:
                # No duplicate keys
                raise ValueError
            self.result[key] = self.translator.translate(self.composite_id, self.period, item, self.variable.var_id, source_id)
            self.has_result = True
