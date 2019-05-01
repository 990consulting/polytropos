import json
from dataclasses import dataclass, field, fields, MISSING
from typing import List, Dict, Iterator, Any, Set, Iterable, TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from etl4.ontology.track import Track


class Validator:
    @staticmethod
    def validate_sources(variable, sources):
        if variable.track is not None:
            if sources == []:
                return
            if isinstance(variable, Folder):
                raise ValueError
            if (
                variable.parent and
                isinstance(
                    variable.track.variables[variable.parent], GenericList
                )
            ):
                raise ValueError
            for source in sources:
                if source not in variable.track.source.variables:
                    raise ValueError
                if (
                    variable.track.source.variables[source].__class__ !=
                    variable.__class__
                ):
                    raise ValueError

    @staticmethod
    def validate_parent(variable, parent):
        if variable.track is not None:
            if parent == '':
                return
            if parent not in variable.track.variables:
                # invalid parent
                raise ValueError
            if not isinstance(variable.track.variables[parent], Container):
                # parent not container
                raise ValueError
            if (
                isinstance(variable, GenericList) and
                variable.descends_from_list
            ):
                # nested lists
                raise ValueError

    @staticmethod
    def validate_name(variable, name):
        if '/' in name or '.' in name:
            raise ValueError


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
    parent: str = field(default='')

    # The track to which this variable belongs
    track = None
    # The variable id of the variable in the corresponding track
    var_id = None

    def set_track(self, track: "Track"):
        self.track = track

    def set_id(self, var_id: str):
        self.var_id = var_id

    def __setattr__(self, attribute, value):
        if attribute == 'name':
            Validator.validate_name(self, value)
        if attribute == 'sources':
            Validator.validate_sources(self, value)
        if attribute == 'parent':
            Validator.validate_parent(self, value)
        if attribute == 'data_type':
            raise AttributeError
        self.__dict__[attribute] = value

    def alter_list_child_source_mappings(self, list_root: str, child_source_mappings: Iterable[str]):
        pass

    def alter_named_list_child_source_mappings(self, list_root: str, child_source_mappings: Iterable[str]):
        pass

    @property
    def has_targets(self) -> bool:
        """True iff any downstream track contains a variable that depends on this one."""
        pass

    @property
    def descends_from_list(self) -> bool:
        """True iff this or any upstream variable is a list or named list."""
        if not self.parent:
            return False
        parent = self.track.variables[self.parent]
        return isinstance(parent, GenericList) or parent.descends_from_list

    @property
    def relative_path(self) -> Iterator[str]:
        """The path from this node to the nearest list or or root."""
        if not self.parent:
            return [self.name]
        parent = self.track.variables[self.parent]
        if isinstance(parent, GenericList):
            return [self.name]
        parent_path = parent.relative_path
        return parent_path + [self.name]

    @property
    def absolute_path(self) -> Iterator[str]:
        """The path from this node to the root."""
        if not self.parent:
            return [self.name]
        parent_path = self.track.variables[self.parent].absolute_path
        return parent_path + [self.name]

    @property
    def tree(self) -> Dict:
        """A tree representing the descendants of this node. (For UI)"""
        children = [child.tree for child in self.children]
        tree = dict(
            title=self.name,
            varId=self.var_id,
            dataType=self.data_type,
        )
        if children:
            tree['children'] = children
        return tree

    def dump(self) -> Dict:
        """A dictionary representation of this variable."""
        representation = {}
        representation['name'] = self.name
        representation['data_type'] = self.data_type
        representation['sort_order'] = self.sort_order
        for var_field in fields(self):
            if var_field.name == 'name' or var_field.name == 'sort_order':
                continue
            if not getattr(self, var_field.name):
                continue
            representation[var_field.name] = getattr(self, var_field.name)
        return representation

    def dumps(self) -> str:
        """A JSON-compatible representation of this variable. (For serialization.)"""
        return json.dumps(self.dump, indent=4)

    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0, inside_list: int=0) \
            -> Iterator[str]:
        """Provides a list of variable IDs descending from this variable that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        :param inside_list: If -1, include only elements outside lists; if 1, only inside lists.
        """
        pass

    def targets(self) -> Iterator[str]:
        """Returns an iterator of the variable IDs for any variables that DIRECTLY depend on this one in the specified
        stage. Raises an exception if this variable's stage is not the source stage for the specified stage."""
        pass

    @property
    def children(self) -> Iterator["Variable"]:
        return filter(
            lambda variable: variable.parent == self.var_id,
            self.track.variables.values()
        )

    @property
    def data_type(self) -> str:
        return self.__class__.__name__


@dataclass
class Container(Variable):
    pass


@dataclass
class Primitive(Variable):
    # For primitives only, the value expected for this variable in a specified instance hierarchy
    simple_expected_values: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class Integer(Primitive):
    pass


@dataclass
class Text(Primitive):
    pass


@dataclass
class Decimal(Primitive):
    pass


@dataclass
class Unary(Primitive):
    pass


@dataclass
class Binary(Primitive):
    pass


@dataclass
class Currency(Primitive):
    pass


@dataclass
class Phone(Primitive):
    pass


@dataclass
class Email(Primitive):
    pass


@dataclass
class URL(Primitive):
    pass


@dataclass
class Date(Primitive):
    pass


# TODO The following three produce an error in PyCharm (although the code runs). "Inherited non-default arguments
#  defined in Container follows inherited default arguments defined in Variable."
@dataclass
class Folder(Container):
    def targets(self):
        raise AttributeError


@dataclass
class GenericList(Container):
    # For lists and named lists, sources for any list descendents relative to a particular root source.
    source_child_mappings: Dict[str, Dict[str, List[str]]] = field(
        default_factory=dict
    )
    # For lists and named lists, the set of fields for which expected values are to be supplied. (We do not necessarily
    # have expected values for every descendant.) Descendants are identified by their IDs, not their paths.
    list_expected_values_fields: Set[str] = field(
        default_factory=set
    )


@dataclass
class List(GenericList):
    # For lists, a mapping of instance hierarchy ID to set of per-subfield expected values. Note that
    # the set of expected values for a given instance hierarchy may be zero-length (we explicitly expect that the list
    # is empty).
    list_expected_values: Dict[str, Iterable[Dict[str, Any]]] = field(
        default_factory=dict
    )


@dataclass
class NamedList(GenericList):
    # For named lists, a mapping of instance hierarchy ID to a mapping of name to per-subfield expected values. Note
    # that the set of expected values for a given instance hierarchy may be zero-length (we explicitly expect that
    # the named list is empty).
    named_list_expected_values: Dict[str, Dict[str, Dict[str, Any]]] = field(
        default_factory=dict
    )
