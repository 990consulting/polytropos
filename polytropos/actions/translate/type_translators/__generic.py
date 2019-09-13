from typing import Any

from polytropos.actions.translate.type_translators.__base import BaseTypeTranslator
from polytropos.actions.translate.type_translators.__decorator import type_translator
from polytropos.ontology.variable import Variable


@type_translator(Variable)
class GenericTypeTranslator(BaseTypeTranslator[Any, Any]):
    """Translate for primitive (non-container) variables"""

    def initial_result(self) -> Any:
        return None

    def process_source_value(self, source_value: Any, source_id: str) -> None:
        self.result = source_value
        self.has_result = True
        # The search goes in order of source priority. So if a source variable exists, whether or not it's null,
        # that's the translation.
        self.result_is_ready = True
