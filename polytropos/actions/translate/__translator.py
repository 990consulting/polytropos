import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Dict, Optional, Any, Type

from polytropos.actions.translate.__document import SourceNotFoundException, DocumentValueProvider
from polytropos.ontology.track import Track
from polytropos.ontology.variable import Variable


#if TYPE_CHECKING:
#    from polytropos.ontology.variable import Variable

class Translator(Callable):
    registered_type_translators: Dict[Optional[Type], Type] = {}

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
        self.target_variables_by_parent: Dict = defaultdict(list)
        for variable_id, variable in target.items():  # type: str, "Variable"
            self.target_variables_by_parent[variable.parent].append(variable)

        # when failsafe is true exceptions are caught and ignored
        self.failsafe = failsafe

    def create_type_translator(self, document: DocumentValueProvider, variable: "Variable", parent_id: str) -> Callable:
        for variable_type, translator_type in Translator.registered_type_translators.items():
            if variable_type is not None and isinstance(variable, variable_type):
                return translator_type(self, document, variable, parent_id)

        return Translator.registered_type_translators[None](self, document, variable, parent_id)

    # TODO Figure out what classes parent and source_parent are ever allowed to be.
    def __call__(self, document: Dict, parent_id: str = '', source_parent_id: str = '') -> Dict:
        assert document is not None, "Unexpected situation occurred -- study"

        output_document = {}
        # Translate all variables with the same parent
        children = self.target_variables_by_parent[parent_id]
        for variable in children:  # type: "Variable"
            try:
                type_translator = self.create_type_translator(DocumentValueProvider(document), variable, source_parent_id)
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

    @classmethod
    def register_type_translator(cls, variable_type: Optional[Type], translator_type: Type) -> None:
        cls.registered_type_translators[variable_type] = translator_type
