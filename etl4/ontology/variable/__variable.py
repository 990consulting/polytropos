import json
from dataclasses import dataclass, field
from typing import List, Dict, Iterator
from etl4.ontology.schemas import DATA_TYPES
from datetime import datetime

@dataclass
class Variable:
    name: str
    sort_order: int
    notes: str
    earliest_epoch: str
    latest_epoch: str
    sources: List[str] = field(default_factory=list)
    parent: str = field(default_factory=str)
    source_child_mappings: Dict[str, Dict[str, List[str]]] = field(
        default_factory=dict
    )

    def source_of(self, stage: str) -> Iterator[str]:
        """Returns an iterator of the variable IDs for any variables that DIRECTLY depend on this one in the specified
        stage. Raises an exception if this variable's stage is not the source stage for the specified stage."""
        pass

    @property
    def has_targets(self) -> bool:
        """True iff any downstream track contains a variable that depends on this one."""
        pass

    @property
    def descends_from_list(self) -> bool:
        """True iff this or any upstream variable is a list or named list."""
        pass

    @property
    def relative_path(self) -> Iterator[str]:
        """The path from this node to the nearest list or or root."""
        pass

    @property
    def absolute_path(self) -> Iterator[str]:
        """The path from this node to the root."""
        pass

    @property
    def tree(self) -> Dict:
        """A tree representing the descendants of this node. (For UI)"""

    @property
    def as_dict(self) -> Dict:
        """A dictionary representation of this variable."""
        pass

    @property
    def json(self) -> str:
        """A JSON-compatible representation of this variable. (For serialization.)"""
        return json.dumps(self.as_dict)

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0) -> Iterator[str]:
        """Provides a list of variable IDs descending from this variable that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        """
        pass

    @property
    def children(self) -> Iterator["Variable"]:
        pass

@dataclass
class Container(Variable):
    pass


@dataclass
class Integer(Variable):
    pass


@dataclass
class Text(Variable):
    pass


@dataclass
class Decimal(Variable):
    pass


@dataclass
class Unary(Variable):
    pass


@dataclass
class Binary(Variable):
    pass


@dataclass
class Currency(Variable):
    pass


@dataclass
class Phone(Variable):
    pass


@dataclass
class Email(Variable):
    pass


@dataclass
class URL(Variable):
    pass


@dataclass
class Folder(Container):
    pass


@dataclass
class List(Container):
    pass


@dataclass
class NamedList(Container):
    pass


