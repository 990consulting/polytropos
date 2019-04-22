from dataclasses import dataclass, field
from typing import List, Dict
from etl4.ontology.schemas import DATA_TYPES


@dataclass
class Variable:
    name: str
    sort_order: int
    sources: List[str] = field(default_factory=list)
    parent: str = field(default_factory=str)
    source_child_mappings: Dict[str, Dict[str, List[str]]] = field(
        default_factory=dict
    )


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


class Folder(Container):
    pass


class List(Container):
    pass


class NamedList(Container):
    pass


