import logging
import json
import warnings
from collections import defaultdict, deque
from typing import List as ListType, Dict, Iterator, TYPE_CHECKING, Optional, Set, Any, NewType, Iterable, Deque, cast
from functools import partial
from cachetools import cachedmethod
from cachetools.keys import hashkey
from polytropos.util.nesteddicts import path_to_str

if TYPE_CHECKING:
    from polytropos.ontology.track import Track

VariableId = NewType("VariableId", str)

class Validator:
    @staticmethod
    def validate_sources(variable: "Variable", sources: ListType[VariableId], init: bool = False) -> None:
        if not init:
            _check_folder_has_sources(variable, sources)
        if sources:
            for source in sources:
                #_verify_source_parent(variable, source)  # TODO This validation is broken.
                _verify_source_exists(variable, source)
                _verify_source_compatible(variable, source)

    @staticmethod
    def validate_parent(variable: "Variable", parent: Optional[VariableId]) -> None:
        if parent is None:
            return
        if parent == "":
            raise ValueError('Variable "%s" lists its parent as an empty string.' % variable.var_id)
        if parent not in variable.track:
            # invalid parent
            raise ValueError('Variable "%s" lists "%s" as its parent, but variable doesn\'t exist.' % (
                variable.var_id, parent))
        if not isinstance(variable.track[parent], Container):
            # parent not container
            raise ValueError('Variable "%s" lists "%s" as its parent, but that variable isn\'t a container.' % (
                variable.var_id, parent))
        if (
                isinstance(variable, GenericList) and
                variable.descends_from_list
        ):
            logging.debug('Nested list: %s', variable.var_id)

    @staticmethod
    def validate_name(variable: "Variable", name: str) -> None:
        if '/' in name or '.' in name:
            raise ValueError("bad name")
        sibling_names = set(
            variable.track[sibling].name
            for sibling in variable.siblings
            if sibling != variable.var_id
        )
        if name in sibling_names:
            conflicting_sibling = None
            for sibling in variable.siblings:
                if variable.track[sibling].name == name:
                    conflicting_sibling = sibling
                    break
            assert conflicting_sibling is not None
            raise ValueError('Variable "%s" has a name conflict with sibling "%s".' % (variable.var_id,
                                                                                       conflicting_sibling))

    @staticmethod
    def validate_sort_order(variable: "Variable", sort_order: int, adding: bool = False) -> None:
        # TODO Add a validation that every sort order value is unique among siblings
        if sort_order < 0:
            raise ValueError('Variable "%s" has a sort order less than zero.')
        # This line is very slow. Consider adding a cache for variable.siblings.
        max_sort_order = len(list(variable.siblings)) + (1 if adding else 0)
        if sort_order >= max_sort_order:
            raise ValueError('Variable "%s" has a sort order of %i, which exceeds the total number of variables at its '
                             'level in the hierarchy (%i)' % (variable.var_id, variable.sort_order, max_sort_order))

    @staticmethod
    def validate_var_id(var_id: VariableId) -> None:
        if var_id == "":
            raise ValueError("Variable id is an empty string")

    @classmethod
    def validate(cls, variable: "Variable", init: bool = False, adding: bool = False) -> None:
        """Run validation on the variable, init=True disables some of the
        validation that shouldn't run during schema initialization. For
        example, we might create a child before a parent.
        The parameter adding is only used for validating the sort order. We
        need it because when we are adding a new variable the sort order logic
        is slightly different (because we will end up having one more
        sibling"""
        cls.validate_var_id(variable.var_id)
        cls.validate_parent(variable, variable.parent)
        cls.validate_name(variable, variable.name)

        if variable.track.source is not None:
            cls.validate_sources(variable, variable.sources, init)

        # TODO This line is extremely slow. I suspect that putting a cache on 'Variable.children' would solve it
        cls.validate_sort_order(variable, variable.sort_order, adding)


class Variable:
    def __init__(self, track: "Track", var_id: VariableId, name: str, sort_order: int,
                 metadata: Optional[Dict[str, Any]] = None,
                 sources: Optional[ListType[VariableId]] = None, parent: Optional[VariableId] = None):

        self.initialized = False

        self.data_type = self.__class__.__name__

        # The track to which this variable belongs
        self.track: "Track" = track

        # Used for single dispatch type situations, as well as for schema reports.
        self.data_type = self.__class__.__name__

        # The variable id of the variable in the corresponding track.
        # WARNING! The variable ID _MUST_ be unique within the schema, or terrible things will happen!
        self.var_id: VariableId = var_id

        # The name of the node, as used in paths. Not to be confused with its ID, which is path-immutable.
        self.name: str = name

        # The order that this variable appears in instance hierarchies.
        self.sort_order: int = sort_order

        # Metadata: any information about the variable that the operator chooses to include.
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}

        # The variable IDs (not names!) from the preceding stage from which to derive values for this variable, if any.
        self.sources: ListType[VariableId] = sources if sources is not None else []

        # The container variable above this variable in the hierarchy, if any.
        self.parent: Optional[VariableId] = parent

        self._cache: Dict = {}

        self.initialized = True

    def __hash__(self) -> int:
        return hash(self.var_id) if self.var_id is not None else 0

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.var_id == self.var_id

    def __setattr__(self, attribute: str, value: Any) -> None:
        if attribute != "initialized" and self.initialized:
            raise AttributeError("Variables are immutable at runtime and must be edited offline.")

        self.__dict__[attribute] = value

    def validate_attribute_value(self, attribute: str, value: Any) -> Any:
        if attribute == 'var_id':
            Validator.validate_var_id(value)
        elif attribute == 'name':
            Validator.validate_name(self, value)
        elif attribute == 'sources':
            Validator.validate_sources(self, value)
            if self.track and isinstance(self, GenericList):
                child_sources: Dict[VariableId, ListType[Variable]] = defaultdict(list)
                for child in self.children:
                    for source_id in child.sources:
                        child_sources[source_id].append(child)
                safe = set()
                assert self.track.source is not None
                for source_id in value:
                    source_var = self.track.source[source_id]
                    for child_source in child_sources:
                        if source_var.is_ancestor_of(child_source):
                            safe.add(child_source)
                for child_source, children in child_sources.items():
                    if child_source not in safe:
                        for child in children:
                            child.sources.remove(child_source)
        elif attribute == 'parent':
            Validator.validate_parent(self, value)
        elif attribute == 'sort_order':
            Validator.validate_sort_order(self, value)
        elif attribute == 'data_type':
            raise AttributeError

        return value

    @property
    def temporal(self) -> bool:
        return self.track.schema is not None and self.track.schema.is_temporal(self.var_id)

    @property  # type: ignore # Decorated property not supported
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'siblings'))
    def siblings(self) -> Iterable[VariableId]:
        if self.parent is None:
            return list(map(lambda root: root.var_id, self.track.roots))
        return list(map(
            lambda child: child.var_id,
            self.track[self.parent].children
        ))

    @property  # type: ignore
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'descends_from_list'))
    def descends_from_list(self) -> bool:
        """True iff this or any upstream variable is a list or keyed list."""
        if not self.parent:
            return False
        parent = self.track[self.parent]
        return isinstance(parent, GenericList) or parent.descends_from_list

    @property  # type: ignore
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'nearest_list'))
    def nearest_list(self) -> VariableId:
        if not self.descends_from_list:
            raise AttributeError
        parent_id: VariableId = cast(VariableId, self.parent)
        parent = self.track[parent_id]
        if isinstance(parent, GenericList):
            return parent_id
        else:
            return parent.nearest_list

    @property  # type: ignore # Decorated property not supported
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

    @property  # type: ignore # Decorated property not supported
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'absolute_path'))
    def absolute_path(self) -> ListType[str]:
        """The path from this node to the root."""
        if not self.parent:
            return [self.name]
        parent_path: ListType = self.track[self.parent].absolute_path
        return parent_path + [self.name]

    @property  # type: ignore # Decorated property not supported
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'tree'))
    def tree(self) -> Dict:
        """A tree representing the descendants of this node. (For UI)"""
        children = [
            child.tree
            for child in sorted(
                self.children, key=lambda child: child.sort_order
            )
        ]
        tree: Dict[str, Any] = dict(
            title=self.name,
            varId=self.var_id,
            dataType=self.data_type,
        )
        if children:
            tree['children'] = children
        if len(self.metadata) > 0:
            tree["metadata"] = self.metadata
        if len(self.sources) > 0:
            tree["sources"] = self.sources

        return tree

    def dump(self) -> Dict:
        """A dictionary representation of this variable."""
        representation = {
            'name': self.name,
            'data_type': self.data_type,
            'sort_order': self.sort_order
        }
        for field_name, field_value in vars(self).items():
            if field_name in {'name', 'sort_order', 'track', 'initialized', 'var_id', '_cache'}:
                continue
            if field_value:
                representation[field_name] = field_value
        return representation

    def dumps(self) -> str:
        """A JSON-compatible representation of this variable. (For serialization.)"""
        return json.dumps(self.dump(), indent=4)

    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'check_ancestor'))
    def is_ancestor_of(self, child_id: VariableId, stop_at_list: bool = False) -> bool:
        variable = self.track[child_id]
        if variable.parent is None:
            return False
        if (
                stop_at_list and
                isinstance(self.track[variable.parent], GenericList)
        ):
            return False
        if variable.parent == self.var_id:
            return True
        return self.is_ancestor_of(variable.parent)

    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'first_list_ancestor'))
    def get_first_list_ancestor(self) -> Optional["Variable"]:
        parent_id = self.parent
        if parent_id is None:
            return None
        parent = self.track[parent_id]
        if isinstance(parent, GenericList):
            return parent
        return parent.get_first_list_ancestor()

    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'descendants_that'))
    def descendants_that(self, data_type: str=None, container: int=0, inside_list: int=0) \
            -> Iterable[VariableId]:
        """Provides a list of variable IDs descending from this variable that meet certain criteria.
        :param data_type: The type of descendant to be found.
        :param container: If -1, include only primitives; if 1, only containers.
        :param inside_list: If -1, include only elements outside lists; if 1, only inside lists.
        """
        ret: Deque[VariableId] = deque()
        for variable_id in self.track.descendants_that(
            data_type, container, inside_list
        ):
            if self.is_ancestor_of(variable_id, stop_at_list=True):
                ret.append(variable_id)
        return list(ret)

    @property   # type: ignore # Decorated property not supported
    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'targets'))
    def children(self) -> Iterable["Variable"]:
        # TODO Consider caching the list of children for each variable in Track.
        return list(filter(
            lambda variable: variable.parent == self.var_id,
            self.track.values()
        ))

    @cachedmethod(lambda self: self._cache, key=partial(hashkey, 'ancestors'))
    def ancestors(self, parent_id_to_stop: Optional[VariableId]) -> Iterable["Variable"]:
        """Returns an iterator of ancestors (self, self.parent, self.parent.parent, etc).
        The first item - the current variable.
        If the parent_id_to_stop parameter is None all ancestors are returned.
        Otherwise the last item is the ancestor with parent identifier equal to parent_id_to_stop."""
        ret: Deque[Variable] = deque()
        current = self
        ret.append(current)
        while current.parent is not None and current.parent != parent_id_to_stop:
            current = self.track[current.parent]
            ret.append(current)
        return list(ret)

    @property
    def transient(self) -> bool:
        """Transient if a variable has the key "transient" in its metadata dictionary
        and the value of "transient" does not represent false
        (i.e., anything except null, empty string, "false", "no", 0, or boolean false)"""
        return "transient" in self.metadata and self.metadata["transient"] not in [None, "", 0, False, "false", "no"]

    @property
    def has_transient_ancestor(self) -> bool:
        current: Variable = self
        while current.parent is not None:
            current = self.track[current.parent]
            if current.transient:
                return True
        return False


class Container(Variable):
    pass

class MultipleText(Variable):
    pass

class Folder(Container):
    pass

class GenericList(Container):
    pass

class List(GenericList):
    pass

class KeyedList(GenericList):
    pass

def _incompatible_type(source_var: Variable, variable: Variable) -> bool:
    if variable.__class__ == List:
        if source_var.__class__ not in {List, Folder}:
            return True
    elif source_var.__class__ != variable.__class__:
        return True
    return False

def _check_folder_has_sources(variable: "Variable", sources: ListType[VariableId]) -> None:
    if len(sources) > 0 and isinstance(variable, Folder):
        var_id: VariableId = variable.var_id
        source_str = ", ".join(sources)
        msg_template: str = 'Folders can\'t have sources, but variable "%s" is a Folder and lists the following ' \
                            'sources: %s'
        raise ValueError(msg_template % (var_id, source_str))

# TODO This should work, but it doesn't
def _verify_source_parent(variable: "Variable", source_var_id: VariableId) -> None:
    list_ancestor: Optional["Variable"] = variable.get_first_list_ancestor()
    if list_ancestor is None:
        return
    parent_sources: Set[VariableId] = set(list_ancestor.sources)
    assert variable.track.source is not None
    source: "Variable" = variable.track.source[source_var_id]
    while source.parent is not None and source.var_id not in parent_sources:
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

def _verify_source_exists(variable: "Variable", source_var_id: VariableId) -> None:
    assert variable.track.source is not None
    if source_var_id not in variable.track.source:
        var_id: VariableId = variable.var_id
        source_track_name: str = variable.track.source.name
        msg_template: str = 'Variable "%s" is attempting to add source variable "%s", which does not exist in the ' \
                            'source track "%s"'
        raise ValueError(msg_template % (var_id, source_var_id, source_track_name))

def _verify_source_compatible(variable: "Variable", source_var_id: VariableId) -> None:
    assert variable.track.source is not None
    source_var = variable.track.source[source_var_id]
    if _incompatible_type(source_var, variable):
        var_id: VariableId = variable.var_id
        var_type: str = variable.__class__.__name__
        source_var_type: str = source_var.__class__.__name__
        msg_template: str = 'Variable "%s" (%s) is attempting to add incompatible source variable %s (%s)'
        raise ValueError(msg_template % (var_id, var_type, source_var_id, source_var_type))
