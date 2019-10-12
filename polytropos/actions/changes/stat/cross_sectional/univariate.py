from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any, List as ListType, Dict, Sequence, Tuple

from polytropos.tools.qc import POLYTROPOS_NA

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId, Variable, Container, KeyedList, List
from polytropos.util import nesteddicts
from polytropos.util.nesteddicts import MissingDataError

@dataclass  # type: ignore
class CrossSectionalUnivariateStatistic(Change, ABC):  # type: ignore
    """Calculate a univariate statistic based on all observations in a List or KeyedList."""

    # A List or KeyedList containing the observations
    subjects: VariableId

    # A primitive whose value is to be considered across all cases.
    argument: VariableId

    # Where to put the calculated value.
    value_target: VariableId

    def __post_init__(self) -> None:
        subjects_var: Variable = self.schema.get(self.subjects)

        if not subjects_var.temporal:
            raise ValueError("Immutable support for cross-sectional statisitics not yet implemented.")

class CrossSectionalMean(CrossSectionalUnivariateStatistic):

    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

class CrossSectionalMedian(CrossSectionalUnivariateStatistic):

    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

@dataclass  # type: ignore
class _CrossSectionalMinMax(CrossSectionalUnivariateStatistic, ABC):  # type: ignore

    # A field by means of which to identify each subject. If the subjects are in a KeyedList, this must be left blank.
    # If left blank for a List, identifiers will not be tracked.
    identifier: Optional[VariableId] = field(default=None)

    # Where to put the identifier of the resulting subject.
    identifier_target: Optional[VariableId] = field(default=None)

    def __post_init__(self) -> None:
        subjects_var: Variable = self.schema.get(self.subjects)
        if not isinstance(subjects_var, (List, KeyedList)):
            raise ValueError("Subject containers must be Lists or KeyedLists.")

        if isinstance(subjects_var, List) and self.identifier is not None and self.identifier_target is None:
            raise ValueError("Identifier specified without a target.")

        if isinstance(subjects_var, List) and self.identifier is None and self.identifier_target is not None:
            raise ValueError("Identifier target specified without an identifier.")

        if isinstance(subjects_var, KeyedList) and self.identifier is not None:
            raise ValueError("Explicit identitifer specified for a KeyedList, which have built-in identifiers.")

    @abstractmethod
    def _cmp(self, argument: Any, limit: Any) -> bool:
        pass

    def _sets_new_limit(self, argument: Optional[Any], limit: Optional[Any]) -> bool:
        if argument is None:
            return False

        if limit is None:
            return True

        return self._cmp(argument, limit)

    def _handle_list(self, content: Dict) -> Tuple[Optional[Any], Optional[str]]:
        limit: Optional[Any] = None
        arg_limit: Optional[str] = POLYTROPOS_NA

        subjects_path: ListType[str] = self.schema.get(self.subjects).absolute_path
        subjects: ListType[Dict] = nesteddicts.get(content, subjects_path, default=None)
        if subjects is None:
            return limit, arg_limit

        arg_path: ListType[str] = self.schema.get(self.argument).relative_path
        if self.identifier is not None:
            id_path: ListType[str] = self.schema.get(self.identifier).relative_path
        for subject in subjects:
            try:
                argument: Optional[Any] = nesteddicts.get(subject, arg_path)
            except MissingDataError:
                continue
            if self._sets_new_limit(argument, limit):
                limit = argument
                if self.identifier is not None:
                    # noinspection PyUnboundLocalVariable
                    arg_limit = nesteddicts.get(subject, id_path, default=POLYTROPOS_NA)

        return limit, arg_limit

    def _handle_keyed_list(self, content: Dict) -> Tuple[Optional[Any], Optional[str]]:
        limit: Optional[Any] = None
        arg_limit: Optional[str] = POLYTROPOS_NA

        subjects_path: ListType[str] = self.schema.get(self.subjects).absolute_path
        subjects: Dict[str, Dict] = nesteddicts.get(content, subjects_path, default=None)
        if subjects is None:
            return limit, arg_limit

        arg_path: ListType[str] = self.schema.get(self.argument).relative_path
        for identifier, subject in subjects.items():
            try:
                argument: Optional[Any] = nesteddicts.get(subject, arg_path)
            except MissingDataError:
                continue
            if self._sets_new_limit(argument, limit):
                limit = argument
                arg_limit = identifier

        return limit, arg_limit

    def _assign(self, content: Dict, limit: Optional[Any], arg_limit: Optional[str]) -> None:
        if limit is None:
            return
        target_path: ListType[str] = self.schema.get(self.value_target).absolute_path
        nesteddicts.put(content, target_path, limit)

        if self.identifier_target is not None and arg_limit != POLYTROPOS_NA:
            id_target_path: ListType[str] = self.schema.get(self.identifier_target).absolute_path
            nesteddicts.put(content, id_target_path, arg_limit)

    def __call__(self, composite: Composite) -> None:
        subjects_var: Variable = self.schema.get(self.subjects)
        # Will be trivial to implement immutable support when needed
        for period in composite.periods:
            content: Dict = composite.content[period]

            if subjects_var.data_type == "List":
                limit, arg_limit = self._handle_list(composite.content[period])
            elif subjects_var.data_type == "KeyedList":
                limit, arg_limit = self._handle_keyed_list(composite.content[period])
            else:
                raise ValueError

            self._assign(content, limit, arg_limit)

class CrossSectionalMinimum(_CrossSectionalMinMax):  # type: ignore
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument < limit

class CrossSectionalMaximum(_CrossSectionalMinMax):  # type: ignore
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument > limit
