from abc import ABC, abstractmethod
from typing import Any, Optional, Iterator, Tuple, List as ListType, Dict, Union, cast

from polytropos.tools.qc import POLYTROPOS_NA

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import VariableId, Variable, List, KeyedList, Primitive
from polytropos.util import nesteddicts
from polytropos.util.nesteddicts import MissingDataError

class ValueIterator(ABC):
    @abstractmethod
    def __call__(self, content: Dict) -> Iterator[Tuple[Optional[Any], Optional[str]]]:
        pass

class KeyedListIterator(ValueIterator):
    def __init__(self, schema: Schema, keyed_list_id: VariableId, argument_id: VariableId):
        self.subjects_path: ListType[str] = schema.get(keyed_list_id).absolute_path
        self.arg_path: ListType[str] = schema.get(argument_id).relative_path

    def __call__(self, content: Dict) -> Iterator[Tuple[Optional[Any], Optional[str]]]:
        subjects: Dict[str, Dict] = nesteddicts.get(content, self.subjects_path, default=None)
        if subjects is None:
            return

        for identifier, subject in subjects.items():
            try:
                value: Optional[Any] = nesteddicts.get(subject, self.arg_path)
            except MissingDataError:
                continue
            yield value, identifier

class ListIterator(ValueIterator):
    def __init__(self, schema: Schema, list_id: VariableId, argument_id: VariableId,
                 identifier_id: Optional[VariableId]):

        self.subjects_path: ListType[str] = schema.get(list_id).absolute_path
        self.arg_path: ListType[str] = schema.get(argument_id).relative_path

        self.identifier_path: Optional[ListType[str]] = None

        if identifier_id is not None:
            self.identifier_path = schema.get(identifier_id).relative_path

    def __call__(self, content: Dict) -> Iterator[Tuple[Optional[Any], Optional[str]]]:
        subjects: ListType[Dict] = nesteddicts.get(content, self.subjects_path, default=None)
        if subjects is None:
            return

        for subject in subjects:
            try:
                value: Optional[Any] = nesteddicts.get(subject, self.arg_path)
            except MissingDataError:
                continue
            identifier: Optional[str] = POLYTROPOS_NA
            if self.identifier_path is not None:
                identifier = nesteddicts.get(subject, self.identifier_path, default=POLYTROPOS_NA)
            yield value, identifier

def _ad_hoc_subjects(subjects: Union[ListType, Dict]) -> Iterator[Tuple[VariableId, str]]:
    if isinstance(subjects, list):
        for subject in subjects:
            yield subject, subject

    elif isinstance(subjects, dict):
        yield from subjects.items()

    else:
        raise ValueError

class AdHocIterator(ValueIterator):
    def __init__(self, schema: Schema, subjects: Union[ListType, Dict]):
        self.subjects: Dict[str, ListType[str]] = {}

        data_type: Optional[str] = None
        for subject_id, identifier in _ad_hoc_subjects(subjects):
            subject: Variable = schema.get(subject_id)
            if not isinstance(subject, Primitive):
                raise ValueError('Non-primitive variable "%s" supplied as ad-hoc cross-sectional subject.' %
                                 subject_id)
            subject_data_type: str = subject.data_type
            if data_type is None:
                data_type = subject_data_type
            if subject_data_type != data_type:
                raise ValueError('Attempting to compare different data types (%s and %s)' %
                                 (data_type, subject_data_type))
            if identifier in self.subjects:
                raise ValueError('Identifier "%s" supplied twice in ad-hoc cross sectional subjects.' % identifier)
            self.subjects[identifier] = subject.absolute_path

    def __call__(self, content: Dict) -> Iterator[Tuple[Optional[Any], Optional[str]]]:
        for identifier, argument_path in self.subjects.items():
            try:
                value: Optional[Any] = nesteddicts.get(content, argument_path)
            except MissingDataError:
                continue
            yield value, identifier

def value_iterator(schema: Schema, subjects: Any, argument_id: Optional[VariableId],
                   identifier_id: Optional[VariableId], identifier_target_id: Optional[VariableId]) -> ValueIterator:

    if isinstance(subjects, (list, dict)):
        if argument_id is not None:
            raise ValueError("'argument' parameter specified for an ad-hoc grouping of variables. This parameter is "
                             "only for cross-sectional analysis across List and KeyedList containers.")

        if identifier_id is not None:
            raise ValueError("'identifier' parameter specified for an ad-hoc grouping of variables. This parameter is "
                             "only for cross-sectional analysis across List containers.")

        return AdHocIterator(schema, subjects)

    subjects_var_id: VariableId = cast(VariableId, subjects)
    subjects_var: Variable = schema.get(subjects_var_id)

    if isinstance(subjects_var, List) and identifier_id is not None and identifier_target_id is None:
        raise ValueError("Identifier specified without a target.")

    if isinstance(subjects_var, List) and identifier_id is None and identifier_target_id is not None:
        raise ValueError("Identifier target specified without an identifier.")

    if isinstance(subjects_var, KeyedList) and identifier_id is not None:
        raise ValueError("Explicit identifier specified for a KeyedList, which have built-in identifiers.")

    # Sometimes I hate MyPy
    not_optional_arg_id: VariableId = cast(VariableId, argument_id)

    if isinstance(subjects_var, List):
        return ListIterator(schema, subjects_var_id, not_optional_arg_id, identifier_id)

    if isinstance(subjects_var, KeyedList):
        return KeyedListIterator(schema, subjects_var_id, not_optional_arg_id)

    raise ValueError('The "subject" parameter must either be a list of primitive variables or the id of a List or '
                     'KeyedList.')
