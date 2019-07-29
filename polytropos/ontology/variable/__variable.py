import logging
import json
from abc import abstractmethod
from dataclasses import dataclass, field, fields
from collections import defaultdict
from typing import List as ListType, Dict, Iterator, TYPE_CHECKING, Optional, Set, Any
from functools import partial
from cachetools import cachedmethod
from cachetools.keys import hashkey
from polytropos.util.nesteddicts import path_to_str
from datetime import datetime

if TYPE_CHECKING:
    from polytropos.ontology.track import Track

class Validator:
    @staticmethod
    def validate_sources(variable: "Variable", sources: ListType[str], init: bool=False):
        if variable.track is not None:
            if not init:
                _check_folder_has_sources(variable, sources)
            if sources:
                for source in sources:
                    #_verify_source_parent(variable, source)
                    _verify_source_exists(variable, source)
                    _verify_source_compatible(variable, source)

    @staticmethod
    def validate_parent(variable, parent):
        if variable.track is not None:
            if parent == '':
                return
            if parent not in variable.track:
                # invalid parent
                raise ValueError('Nonexistent parent')
            if not isinstance(variable.track[parent], Container):
                # parent not container
                raise ValueError('Parent is not a container')
            if (
                    isinstance(variable, GenericList) and
                    variable.descends_from_list
            ):
                logging.debug('Nested list: %s', variable)

    @staticmethod
    def validate_name(variable, name):
        if '/' in name or '.' in name:
            raise ValueError
        if variable.track is not None:
            sibling_names = set(
                variable.track[sibling].name
                for sibling in variable.siblings
                if sibling != variable.var_id
            )
            if name in sibling_names:
                raise ValueError('Duplicate name with siblings')

    @staticmethod
    def validate_sort_order(variable, sort_order, adding=False):
        if sort_order < 0:
            raise ValueError
        if variable.track is not None:
            # This line is very slow. Consider adding a cache for variable.siblings.
            if sort_order >= len(list(variable.siblings)) + (1 if adding else 0):
                raise ValueError('Invalid sort order')

    @classmethod
    def validate(cls, variable, init=False, adding=False):
        """Run validation on the variable, init=True disables some of the
        validation that shouldn't run during schema initialization. For
        example, we might create a child before a parent.
        The parameter adding is only used for validating the sort order. We
        need it because when we are adding a new variable the sort order logic
        is slightly different (because we will end up having one more
        sibling"""
        cls.validate_parent(variable, variable.parent)
        cls.validate_name(variable, variable.name)

        if variable.track.source is not None:
            cls.validate_sources(variable, variable.sources, init)

        # TODO This line is extremely slow. I suspect that putting a cache on 'Variable.children' would solve it
        cls.validate_sort_order(variable, variable.sort_order, adding)


@dataclass
class Variable:
    # The name of the node, as used in paths. Not to be confused with its ID, which is path-immutable.
    name: str

    # The order that this variable appears in instance hierarchies.
    sort_order: int

    # Metadata: any information about the variable that the operator chooses to include.
    notes: str = field(default=None)

    # An alphabetically sortable indicator of when this field first came into use.
    earliest_epoch: str = field(default=None)

    # An alphabetically sortable indicator of when this field ceased to be used.
    latest_epoch: str = field(default=None)

    # Descriptions of the variable -- used in various situations
    short_description: str = field(default=None)
    long_description: str = field(default=None)

    # The variable IDs (not names!) from the preceding stage from which to derive values for this variable, if any.
    sources: ListType[str] = field(default_factory=list)

    # The container variable above this variable in the hierarchy, if any.
    parent: str = field(default='')

    # The track to which this variable belongs
    track = None

    # The variable id of the variable in the corresponding track.
    # WARNING! The variable ID _MUST_ be unique within the schema, or terrible things will happen!
    var_id = None

    _cache: Dict = field(init=False, default_factory=dict)

    def __hash__(self) -> str:
        return self.var_id

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and other.var_id == self.var_id

    def set_track(self, track: "Track"):
        self.track = track

    def set_id(self, var_id: str):
        self.var_id = var_id

    def __setattr__(self, attribute, value):
        if attribute == 'name':
            Validator.validate_name(self, value)
        if attribute == 'sources':
            Validator.validate_sources(self, value)
            if self.track and isinstance(self, GenericList):
                child_sources = defaultdict(list)
                for child in self.children:
                    for source in child.sources:
                        child_sources[source].append(child)
                safe = set()
                for source in value:
                    source_var = self.track.source[source]
                    for child_source in child_sources:
                        if source_var.check_ancestor(child_source):
                            safe.add(child_source)
                for child_source, children in child_sources.items():
                    if child_source not in safe:
                        for child in children:
                            child.sources.remove(child_source)
        if attribute == 'parent':
            Validator.validate_parent(self, value)
        if attribute == 'sort_order':
            Validator.validate_sort_order(self, value)
        if attribute in {'notes', 'earliest_epoch', 'latest_epoch', 'short_description', 'long_description'}:
            if value is not None:
                self.__dict__[attribute] = value.strip()
                return
        if attribute == 'data_type':
            raise AttributeError
        if self.track and attribute in {'sort_order', 'parent', 'name'}:
            self.track.invalidate_variables_cache()
        self.__dict__[attribute] = value

    def invalidate_cache(self):
        logging.debug("Invaliding cache for variable %s." % self.var_id)
        self._cache.clear()

    def update_sort_order(self, old_order=None, new_order=None):
        if old_order is None:
            old_order = len(list(self.siblings)) + 1
        if new_order is None:
            new_order = len(list(self.siblings)) + 1
        for sibling in self.siblings:
            if sibling == self.var_id:
                continue
            diff = 0
            if self.track[sibling].sort_order >= new_order:
                diff += 1
            if self.track[sibling].sort_order >= old_order:
                diff -= 1
            self.track[sibling].__dict__['sort_order'] += diff

    @property
    def temporal(self) -> bool:
        return self.track.schema.is_temporal(self.var_id)

    @property
    def siblings(self) -> Iterator[str]:
        if self.parent == '':
            return map(lambda root: root.var_id, self.track.roots)
        return map(
            lambda child: child.var_id,
            self.track[self.parent].children
        )

    @property
    def has_targets(self) -> bool:
        """True iff any downstream track contains a variable that depends on this one."""
        return any(self.targets())

    @property
    def descends_from_list(self) -> bool:
        """True iff this or any upstream variable is a list or named list."""
        if not self.parent:
            return False
        parent = self.track[self.parent]
        return isinstance(parent, GenericList) or parent.descends_from_list

    @property
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'relative_path'))
    def relative_path(self) -> ListType[str]:
        """The path from this node to the nearest list or or root."""
        if not self.parent:
            return [self.name]
        parent: "Variable" = self.track[self.parent]
        if isinstance(parent, GenericList):
            return [self.name]
        parent_path: ListType = parent.relative_path
        return parent_path + [self.name]

    @property
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'absolute_path'))
    def absolute_path(self) -> ListType[str]:
        """The path from this node to the root."""
        if not self.parent:
            return [self.name]
        parent_path: ListType = self.track[self.parent].absolute_path
        return parent_path + [self.name]

    @property
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'tree'))
    def tree(self) -> Dict:
        """A tree representing the descendants of this node. (For UI)"""
        children = [
            child.tree
            for child in sorted(
                self.children, key=lambda child: child.sort_order
            )
        ]
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
        representation = {
            'name': self.name,
            'data_type': self.data_type,
            'sort_order': self.sort_order
        }
        for var_field in fields(self):
            if var_field.name == 'name' or var_field.name == 'sort_order':
                continue
            if not getattr(self, var_field.name):
                continue
            representation[var_field.name] = getattr(self, var_field.name)
        return representation

    def dumps(self) -> str:
        """A JSON-compatible representation of this variable. (For serialization.)"""
        return json.dumps(self.dump(), indent=4)

    def check_ancestor(self, child, stop_at_list: bool = False) -> bool:
        variable = self.track[child]
        if variable.parent == '':
            return False
        if (
                stop_at_list and
                isinstance(self.track[variable.parent], GenericList)
        ):
            return False
        if variable.parent == self.var_id:
            return True
        return self.check_ancestor(variable.parent)

    def get_first_list_ancestor(self):
        parent_id = self.parent
        if parent_id == '':
            return None
        parent = self.track[parent_id]
        if isinstance(parent, GenericList):
            return parent
        return parent.get_first_list_ancestor()

    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'descendants_that'))
    def descendants_that(self, data_type: str=None, targets: int=0, container: int=0, inside_list: int=0) \
            -> Iterator[str]:
        """Provides a list of variable IDs descending from this variable that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param targets: If -1, include only variables that lack targets; if 1, only variables without targets.
        :param container: If -1, include only primitives; if 1, only containers.
        :param inside_list: If -1, include only elements outside lists; if 1, only inside lists.
        """
        for variable_id in self.track.descendants_that(
            data_type, targets, container, inside_list
        ):
            if self.check_ancestor(variable_id, stop_at_list=True):
                yield variable_id

    def targets(self) -> Iterator[str]:
        """Returns an iterator of the variable IDs for any variables that DIRECTLY depend on this one in the specified
        stage. Raises an exception if this variable's stage is not the source stage for the specified stage."""
        if self.track.target:
            for variable_id, variable in self.track.target.items():
                if self.var_id in variable.sources:
                    yield variable_id

    @property
    def children(self) -> Iterator["Variable"]:
        # TODO Consider caching the list of children for each variable in Track.
        return filter(
            lambda variable: variable.parent == self.var_id,
            self.track.values()
        )

    @property
    def data_type(self) -> str:
        return self.__class__.__name__


@dataclass
class Container(Variable):
    pass


@dataclass
class Primitive(Variable):
    @abstractmethod
    def cast(self, value: Optional[Any]) -> Optional[Any]:
        pass

@dataclass
class Integer(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[int]:
        if value is None or value == "":
            return None
        return int(value)

@dataclass
class Text(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

@dataclass
class Decimal(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[float]:
        if value is None or value == "":
            return None
        return float(value)

@dataclass
class Unary(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[bool]:
        if value is None or value == "":
            return None
        if value is True:
            return True
        if not (isinstance(value, str) and value.lower() == "x"):
            raise ValueError
        return True


@dataclass
class Binary(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[bool]:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return value
        vl = value.lower()
        if vl in {"1", "true"}:
            return True
        if vl in {"0", "false"}:
            return False
        raise ValueError


@dataclass
class Currency(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[float]:
        if value is None or value == "":
            return None
        return float(value)

@dataclass
class Phone(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

@dataclass
class Email(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

@dataclass
class URL(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[str]:
        if value is None or value == "":
            return None
        return str(value)

@dataclass
class Date(Primitive):
    def cast(self, value: Optional[Any]) -> Optional[str]:
        if value is None or value in {"", "000000"}:
            return None
        if len(value) == 6 and value.isdecimal():
            year: str = value[:4]
            month: str = value[4:]
            return "%s-%s-01" % (year, month)

        if len(value) >= 10:
            retained = value[:10]

            # Will raise a ValueError if unexpected content
            datetime.strptime(retained, "%Y-%m-%d")

            return retained

        raise ValueError

@dataclass
class Folder(Container):
    @property
    def has_targets(self):
        return False

    def targets(self):
        raise AttributeError


@dataclass
class GenericList(Container):
    pass


@dataclass
class List(GenericList):
    pass

@dataclass
class NamedList(GenericList):
    pass

def _incompatible_type(source_var: Variable, variable: Variable):
    if variable.__class__ == List:
        if source_var.__class__ not in {List, Folder}:
            return True
    elif source_var.__class__ != variable.__class__:
        return True
    return False

def _check_folder_has_sources(variable: "Variable", sources: ListType[str]):
    if sources is not None and isinstance(variable, Folder):
        var_id: str = variable.var_id
        source_str = ", ".join(sources)
        msg_template: str = 'Folders can\'t have sources, but variable "%s" is a Folder and lists the following ' \
                            'sources: %s'
        raise ValueError(msg_template % (var_id, source_str))

def _verify_source_parent(variable: "Variable", source_var_id: str):
    list_ancestor: Optional["Variable"] = variable.get_first_list_ancestor()
    if list_ancestor is None:
        return
    parent_sources: Set[str] = set(list_ancestor.sources)
    source: "Variable" = variable.track.source[source_var_id]
    while source.parent != '' and source.var_id not in parent_sources:
        source = variable.track.source[source.parent]
    if source.var_id not in parent_sources:
        template: str = 'Variable %s (%s), which descends from %s %s (%s), includes %s (%s) as a source, but that ' \
                        'does not descend from one of the root list\'s sources.'
        msg = template % (
            path_to_str(variable.absolute_path),
            variable.var_id,
            list_ancestor.data_type,
            path_to_str(list_ancestor.absolute_path),
            list_ancestor.var_id,
            path_to_str(source.absolute_path),
            source.var_id
        )
        raise ValueError(msg)

def _verify_source_exists(variable: "Variable", source_var_id: str):
    if source_var_id not in variable.track.source:
        var_id: str = variable.var_id
        source_track_name: str = variable.track.source.name
        msg_template: str = 'Variable "%s" is attempting to add source variable "%s", which does not exist in the ' \
                            'source track "%s"'
        raise ValueError(msg_template % (var_id, source_var_id, source_track_name))

def _verify_source_compatible(variable: "Variable", source_var_id: str):
    source_var = variable.track.source[source_var_id]
    if _incompatible_type(source_var, variable):
        var_id: str = variable.var_id
        var_type: str = variable.__class__.__name__
        source_var_type: str = source_var.__class__.__name__
        msg_template: str = 'Variable "%s" (%s) is attempting to add incompatible source variable %s (%s)'
        raise ValueError(msg_template % (var_id, var_type, source_var_id, source_var_type))
