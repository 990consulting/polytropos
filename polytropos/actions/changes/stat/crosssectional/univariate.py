from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from polytropos.actions.evolve import Change
from polytropos.ontology.composite import Composite
from polytropos.ontology.variable import VariableId

@dataclass
class CrossSectionalUnivariateStatistic(Change, ABC):
    """Calculate a univariate statistic based on all observations in a List or KeyedList."""

    # A List or KeyedList containing the observations
    subjects: VariableId

    # A primitive whose value is to be considered across all cases.
    argument: VariableId

    # Where to put the calculated value.
    value_target: VariableId

class CrossSectionalMean(CrossSectionalUnivariateStatistic):

    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

class CrossSectionalMedian(CrossSectionalUnivariateStatistic):

    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

@dataclass
class IdentifiedCrossSectionalUnivariateStatistic(CrossSectionalUnivariateStatistic, ABC):
    """A univariate statistic whose output is a particular subject and a value associated with that subject."""

    # A field by means of which to identify each subject. If the subjects are in a KeyedList, this must be left blank.
    # If left blank for a List, identifiers will not be tracked.
    identifier: Optional[VariableId] = field(default=None)

    # Where to put the identifier of the resulting subject.
    identifier_target: Optional[VariableId] = field(default=None)

class CrossSectionalMinimum(IdentifiedCrossSectionalUnivariateStatistic):
    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"

class CrossSectionalMaximum(IdentifiedCrossSectionalUnivariateStatistic):
    def __call__(self, composite: Composite) -> None:
        assert False, "Not yet implemented!"
