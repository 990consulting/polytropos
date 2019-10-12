from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any, List as ListType, Dict, Sequence, Tuple

from polytropos.actions.changes.stat.cross_sectional.iterators import ValueIterator, value_iterator
from polytropos.ontology.schema import Schema

from polytropos.tools.qc import POLYTROPOS_NA

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId
from polytropos.util import nesteddicts

class CrossSectionalUnivariateStatistic(Change, ABC):  # type: ignore
    """Calculate a univariate statistic based on all observations in a List or KeyedList."""

    def __init__(self, schema: Schema, lookups: Dict, subjects: Any, value_target: VariableId,
                 argument: Optional[VariableId]=None, identifier: Optional[VariableId]=None,
                 identifier_target: Optional[VariableId]=None):
        super().__init__(schema, lookups)
        self.iterate_over: ValueIterator = value_iterator(schema, subjects, argument, identifier, identifier_target)
        self.identifier_target: Optional[VariableId] = identifier_target
        self.value_target: Optional[VariableId] = value_target

    def _assign(self, content: Dict, limit: Optional[Any], arg_limit: Optional[str]) -> None:
        if limit is None:
            return
        target_path: ListType[str] = self.schema.get(self.value_target).absolute_path
        nesteddicts.put(content, target_path, limit)

        if self.identifier_target is not None and arg_limit != POLYTROPOS_NA:
            id_target_path: ListType[str] = self.schema.get(self.identifier_target).absolute_path
            nesteddicts.put(content, id_target_path, arg_limit)

class CrossSectionalMean(CrossSectionalUnivariateStatistic):
    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

class CrossSectionalMedian(CrossSectionalUnivariateStatistic):
    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

class _CrossSectionalMinMax(CrossSectionalUnivariateStatistic, ABC):

    @abstractmethod
    def _cmp(self, argument: Any, limit: Any) -> bool:
        pass

    def _sets_new_limit(self, argument: Optional[Any], limit: Optional[Any]) -> bool:
        if argument is None:
            return False

        if limit is None:
            return True

        return self._cmp(argument, limit)

    def _handle(self, content: Dict) -> Tuple[Optional[Any], Optional[str]]:
        limit: Optional[Any] = None
        arg_limit: Optional[str] = POLYTROPOS_NA
        for value, identifier in self.iterate_over(content):
            if self._sets_new_limit(value, limit):
                limit = value
                arg_limit = identifier
        return limit, arg_limit

    def __call__(self, composite: Composite) -> None:
        # Will be trivial to implement immutable support when needed
        for period in composite.periods:
            content: Dict = composite.content[period]
            limit, arg_limit = self._handle(content)
            self._assign(content, limit, arg_limit)

class CrossSectionalMinimum(_CrossSectionalMinMax):  # type: ignore
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument < limit

class CrossSectionalMaximum(_CrossSectionalMinMax):  # type: ignore
    def _cmp(self, argument: Any, limit: Any) -> bool:
        return argument > limit
