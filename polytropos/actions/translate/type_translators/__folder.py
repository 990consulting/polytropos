from typing import Dict, Any

from polytropos.actions.translate.__document import SourceNotFoundException
from polytropos.actions.translate.type_translators.__base import BaseTypeTranslator
from polytropos.actions.translate.type_translators.__decorator import type_translator
from polytropos.ontology.variable import Folder


@type_translator(Folder)
class FolderTranslator(BaseTypeTranslator[Dict[str, Any]]):
    """Translate for folders"""

    def initial_result(self) -> Dict[str, Any]:
        return {}

    def __call__(self) -> Dict[str, Any]:
        # Just translate all variables in the folder
        translated: Dict[str, Any] = self.translator.translate(self.document.document, self.variable.var_id, self.parent_id)

        # If the resulting dictionary is empty, none of the children were found, so don't include the folder at all.
        if len(translated) == 0:
            raise SourceNotFoundException
        return translated
