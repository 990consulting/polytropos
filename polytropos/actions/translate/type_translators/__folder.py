from collections import OrderedDict
from typing import Any, Dict

from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.type_translators.__base import BaseTypeTranslator
from polytropos.actions.translate.type_translators.__decorator import type_translator
from polytropos.ontology.variable import Folder


@type_translator(Folder)
class FolderTranslator(BaseTypeTranslator[Dict[str, Any], "OrderedDict[str, Any]"]):
    """Translate for folders"""

    def initial_result(self) -> "OrderedDict[str, Any]":
        return OrderedDict()

    def __call__(self) -> "OrderedDict[str, Any]":
        # Just translate all variables in the folder
        translated: OrderedDict[str, Any] = self.translator.translate(self.composite_id, self.period, self.document.document, self.variable.var_id, self.parent_id)

        # If the resulting dictionary is empty, none of the children were found, so don't include the folder at all.
        if len(translated) == 0:
            raise SourceNotFoundException
        return translated
