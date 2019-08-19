import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Dict, Optional, Any, Type, List

from polytropos.actions.translate.__document import SourceNotFoundException, DocumentValueProvider
from polytropos.actions.translate.__type_translator_registry import TypeTranslatorRegistry
from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable, VariableId


class Translator:
    """Class in charge of translating documents given a source track and a
    target track"""
    def __init__(self, target: Track, failsafe: bool=False):
        logging.info('Initializing translator for track "%s".' % target.name)
        if failsafe:
            logging.warning("Translation errors will be ignored! Use at your own risk!")

        assert target.source is not None
        self.source: Track = target.source

        # We need to group by variables by parent to be able to efficiently do
        # a recursion in the translate function
        # NB: `defaultdict(list)` means "Create a dictionary that automatically supplies missing values"--very nice
        logging.debug("Grouping variables by parents.")
        self.target_variables_by_parent: Dict[Optional[VariableId], List[Variable]] = defaultdict(list)
        for variable in target.values():  # type: Variable
            self.target_variables_by_parent[variable.parent].append(variable)

        # when failsafe is true exceptions are caught and ignored
        self.failsafe = failsafe

    def create_type_translator(self, document: DocumentValueProvider, variable: Variable, parent_id: Optional[VariableId]) -> Callable:
        type_translator_class: Type = TypeTranslatorRegistry.get_translator_class(variable.__class__)
        return type_translator_class(self, document, variable, parent_id)

    def __call__(self, document: Dict[str, Any], parent_id: Optional[VariableId] = None, source_parent_id: Optional[VariableId] = None) -> Dict[str, Any]:
        return self.translate(document, parent_id, source_parent_id)

    def translate(self, document: Dict[str, Any], parent_id: Optional[VariableId] = None, source_parent_id: Optional[VariableId] = None) -> Dict[str, Any]:
        assert document is not None, "Unexpected situation occurred -- study"
        assert not (parent_id is None and source_parent_id is not None)

        document_value_provider: DocumentValueProvider = DocumentValueProvider(document)
        output_document: Dict[str, Any] = {}
        # Translate all variables with the same parent
        children: List[Variable] = self.target_variables_by_parent[parent_id]
        for variable in children:  # type: Variable
            try:
                type_translator: Callable = self.create_type_translator(document_value_provider, variable, source_parent_id)
                result: Any = type_translator()
                output_document[variable.name] = result
            except SourceNotFoundException:
                continue
            except Exception as e:
                if self.failsafe:
                    logging.error('Error translating variable %s', variable.var_id)
                    continue
                else:
                    raise e
        return output_document
