import json
from dataclasses import dataclass, field
from typing import List, Dict, Iterator, Any, Set, Iterable
from etl4.ontology.schemas import DATA_TYPES
from datetime import datetime

@dataclass
class Variable:
    # The name of the node, as used in paths. Not to be confused with its ID, which is path-invariant.
    name: str

    # The order that this variable appears in instance hierarchies.
    sort_order: int

    # Metadata: any information about the variable that the operator chooses to include.
    notes: str = field(default=None)

    # An alphabetically sortable indicator of when this field first came into use.
    earliest_epoch: str = field(default=None)

    # An alphabetically sortable indicator of when this field ceased to be used.
    latest_epoch: str = field(default=None)

    # The variable IDs (not names!) from the preceding stage from which to derive values for this variable, if any.
    sources: List[str] = field(default_factory=list)

    # The container variable above this variable in the hierarchy, if any.
    parent: str = field(default_factory=str)

    # TODO If it would be possible to move subclass-specific properties to their respective subclasses, I think that
    #  would be nice
    # For lists and named lists, sources for any list descendents relative to a particular root source.
    source_child_mappings: Dict[str, Dict[str, List[str]]] = field(
        default_factory=dict
    )

    # For primitives only, the value expected for this variable in a specified instance hierarchy
    simple_expected_values: Dict[str, Any] = field(
        default_factory=dict
    )

    # For lists and named lists, the set of fields for which expected values are to be supplied. (We do not necessarily
    # have expected values for every descendant.) Descendants are identified by their IDs, not their paths.
    list_expected_values_fields: Set[str] = field(
        default_factory=set
    )

    # For lists, a mapping of instance hierarchy ID to set of per-subfield expected values. Note that
    # the set of expected values for a given instance hierarchy may be zero-length (we explicitly expect that the list
    # is empty).
    list_expected_values: Dict[str, Iterable[Dict[str, Any]]] = field(
        default_factory=dict
    )

    # For named lists, a mapping of instance hierarchy ID to a mapping of name to per-subfield expected values. Note
    # that the set of expected values for a given instance hierarchy may be zero-length (we explicitly expect that
    # the named list is empty).
    named_list_expected_values: Dict[str, Dict[str, Dict[str, Any]]] = field(
        default_factory=dict
    )

    # For lists and named lists, a mapping of
    def source_for_vars_in(self, stage: str) -> Iterator[str]:
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

    def dump(self) -> Dict:
        """A dictionary representation of this variable."""
        pass

    def dumps(self) -> str:
        """A JSON-compatible representation of this variable. (For serialization.)"""
        pass

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

# TODO The following three produce an error in PyCharm (although the code runs). "Inherited non-default arguments
#  defined in Container follows inherited default arguments defined in Variable."
@dataclass
class Folder(Container):
    pass


@dataclass
class List(Container):
    pass


@dataclass
class NamedList(Container):
    pass


