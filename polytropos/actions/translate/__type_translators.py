from abc import abstractmethod
from typing import Any, TypeVar, Generic, List, Dict

from polytropos.actions.translate import Translator
from polytropos.actions.translate.__document import DocumentValueProvider, SourceNotFoundException
from polytropos.ontology.variable import Variable

T = TypeVar('T')


class BaseTypeTranslator(Generic[T]):
    def __init__(self, translator: Translator, document: DocumentValueProvider, variable: Variable, parent_id: str):
        self.translator = translator
        self.document = document
        self.variable = variable
        self.parent_id = parent_id

        self.result: T = self.initial_result()
        self.has_result = False
        self.result_is_ready = False
        self.skip_source_not_found = True

    def __call__(self) -> T:
        if self.variable.sources is None or len(self.variable.sources) == 0:
            raise SourceNotFoundException

        self.initialize()

        # We have to restrict the sources to the descendants of parent
        parent_source = None
        if self.parent_id:
            assert self.variable.track is not None and self.variable.track.source is not None
            parent_source = self.variable.track.source[self.parent_id]
        for source_id in self.variable.sources:
            if parent_source and not parent_source.check_ancestor(source_id):
                continue
            try:
                value = self.variable_value(source_id)
            # If we get a SourceNotFoundError, the source variable simply did not exist
            except SourceNotFoundException:
                if self.skip_source_not_found:
                    continue
                raise
            self.process_found_value(value, source_id)
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

    def process_found_value(self, value: Any, source: str) -> None:
        pass

    def variable_value(self, variable_id: str) -> Any:
        """Function that finds a variable (given its id) in a document."""
        variable = self.translator.source[variable_id]
        return self.document.variable_value(variable, self.parent_id)


class GenericTypeTranslator(BaseTypeTranslator[Any]):
    """Translate for primitive (non-container) variables"""

    def initial_result(self) -> Any:
        return None

    def process_found_value(self, value: Any, source_id: str) -> None:
        self.result = value
        self.has_result = True
        # The search goes in order of source priority. So if a source variable exists, whether or not it's null,
        # that's the translation.
        self.result_is_ready = True


class ListTranslator(BaseTypeTranslator[List]):
    """Translate for lists"""

    def initial_result(self) -> List:
        return []

    def initialize(self) -> None:
        self.has_result = True

    def process_found_value(self, value: Any, source_id: str) -> None:
        # The resulting list is the concatenation of all the translations,
        # source by source

        if value is None:
            raise RuntimeError("I don't think this should be possible, because SourceNotFoundException replaced it")
        # sometimes lists with one element are represented as folders
        if isinstance(value, dict):
            value = [value]
        for item in value:
            # translate the values in the list one by one and add them to
            # the result
            # noinspection PyTypeChecker
            matches = self.translator(item, self.variable.var_id, source_id)
            self.result.append(matches)


class NamedListTranslator(BaseTypeTranslator[Dict]):
    """Translate function for named lists (similar to python dicts), the
    logic is almost the same as for lists but taking care of the keys.
    Raises ValueError on duplicate keys"""

    def initial_result(self) -> Dict:
        return {}

    def initialize(self) -> None:
        self.has_result = True
        self.skip_source_not_found = False

    def process_found_value(self, value: Any, source_id: str) -> None:
        if value is None:
            return

        for key, item in value.items():
            if key in self.result:
                # No duplicate keys
                raise ValueError
            self.result[key] = self.translator(item, self.variable.var_id, source_id)
            self.has_result = True


class FolderTranslator(BaseTypeTranslator[Dict]):
    """Translate for folders"""

    def initial_result(self) -> Dict:
        return {}

    def __call__(self) -> Dict:
        # Just translate all variables in the folder
        candidate = self.translator(self.document.document, self.variable.var_id, self.parent_id)

        # If the resulting dictionary is empty, none of the children were found, so don't include the folder at all.
        if len(candidate) == 0:
            raise SourceNotFoundException
        return candidate
