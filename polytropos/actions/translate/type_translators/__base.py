from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, cast

from polytropos.actions.translate import Translator
from polytropos.actions.translate.__document import DocumentValueProvider, SourceNotFoundException
from polytropos.ontology.variable import Variable, VariableId

TSource = TypeVar('TSource')
TResult = TypeVar('TResult')


@dataclass  # type: ignore # https://github.com/python/mypy/issues/5374
class BaseTypeTranslator(Generic[TSource, TResult]):
    translator: Translator
    composite_id: str
    period: str
    document: DocumentValueProvider
    variable: Variable
    parent_id: Optional[VariableId]

    parent_source: Optional[Variable] = field(default=None, init=False)
    result: TResult = field(default=cast(TResult, None), init=False)
    has_result: bool = field(default=False, init=False)
    result_is_ready: bool = field(default=False, init=False)
    skip_source_not_found: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        if self.parent_id:
            assert self.variable.track.source is not None
            self.parent_source = self.variable.track.source[self.parent_id]

        self.result = self.initial_result()
        self.initialize()

    def __call__(self) -> TResult:
        if len(self.variable.sources) == 0:
            raise SourceNotFoundException

        for source_id in self.variable.sources:  # type: VariableId
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
    def initial_result(self) -> TResult:
        pass

    def initialize(self) -> None:
        pass

    def process_source_value(self, source_value: TSource, source_id: VariableId) -> None:
        pass

    def variable_value(self, variable_id: VariableId) -> TSource:
        """Function that finds a variable (given its id) in a document."""
        variable: Variable = self.translator.source[variable_id]
        return self.document.variable_value(variable, self.parent_id)

    def process_source_variable(self, source_id: VariableId) -> None:
        try:
            source_value: TSource = self.variable_value(source_id)
        # If we get a SourceNotFoundError, the source variable simply did not exist
        except SourceNotFoundException:
            if self.skip_source_not_found:
                return
            raise
        self.process_source_value(source_value, source_id)
