from abc import abstractmethod
from typing import TypeVar, Generic, Any, Optional

from polytropos.actions.translate import Translator
from polytropos.actions.translate.__document import DocumentValueProvider, SourceNotFoundException
from polytropos.ontology.variable import Variable, VariableId

T = TypeVar('T')


class BaseTypeTranslator(Generic[T]):
    def __init__(self, translator: Translator, document: DocumentValueProvider, variable: Variable, parent_id: Optional[VariableId]):
        assert variable.track.source is not None

        self.translator = translator
        self.document = document
        self.variable = variable
        self.parent_id = parent_id
        self.parent_source: Optional[Variable] = variable.track.source[parent_id] if parent_id is not None else None

        self.result: T = self.initial_result()
        self.has_result = False
        self.result_is_ready = False
        self.skip_source_not_found = True

    def __call__(self) -> T:
        if len(self.variable.sources) == 0:
            raise SourceNotFoundException

        self.initialize()

        for source_id in self.variable.sources:
            # We have to restrict the sources to the descendants of parent
            if self.parent_source and not self.parent_source.check_ancestor(source_id):
                continue

            self.process_source_variable(source_id)
            if self.result_is_ready:
                return self.result

        if not self.has_result:
            raise SourceNotFoundException
        return self.result

    @abstractmethod
    def initial_result(self) -> T:
        pass

    def initialize(self) -> None:
        pass

    def process_source_value(self, source_value: T, source_id: VariableId) -> None:
        pass

    def variable_value(self, variable_id: VariableId) -> T:
        """Function that finds a variable (given its id) in a document."""
        variable = self.translator.source[variable_id]
        return self.document.variable_value(variable, self.parent_id)

    def process_source_variable(self, source_id: VariableId) -> None:
        try:
            source_value = self.variable_value(source_id)
        # If we get a SourceNotFoundError, the source variable simply did not exist
        except SourceNotFoundException:
            if self.skip_source_not_found:
                return
            raise
        self.process_source_value(source_value, source_id)
