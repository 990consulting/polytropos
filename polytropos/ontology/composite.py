import copy
from dataclasses import dataclass, field
from typing import Dict, Iterator, Optional, Any, Tuple, List

from polytropos.util.nesteddicts import MissingDataError

from polytropos.util import nesteddicts

from polytropos.ontology.schema import Schema, TrackType
from polytropos.ontology.variable import Variable, VariableId


@dataclass(eq=False)
class Composite:
    schema: Schema
    content: Dict = field(default_factory=dict)
    composite_id: str = field(default="UNDEFINED")

    def as_var(self, var_id: VariableId, **kwargs: Any) -> Variable:
        var: Variable = self.schema.get(var_id, **kwargs)
        if var is None:
            raise ValueError('Unrecognized variable ID "%s"' % var_id)
        return var

    @property
    def periods(self) -> Iterator[str]:
        """Iterate over all of the observation periods contained in this composite."""
        yield from set(self.content.keys()) - {"immutable"}

    # TODO Check that this isn't trying to grab a list descendant
    def get_immutable(self, var_id: VariableId, treat_missing_as_null: bool = False) -> Optional[Any]:
        """Get an immutable variable from this composite."""
        var = self.as_var(var_id, track_type=TrackType.IMMUTABLE)

        path = ["immutable"] + list(var.absolute_path)
        try:
            return nesteddicts.get(self.content, path)
        except MissingDataError as e:
            if treat_missing_as_null:
                return None
            raise e

    # TODO Check that this isn't trying to grab a list descendant
    def get_all_observations(self, var_id: VariableId) -> Iterator[Tuple[str, Any]]:
        """Iterate over all observations of a temporal variable from this composite."""
        var = self.as_var(var_id, track_type=TrackType.TEMPORAL)
        var_path: List = list(var.absolute_path)
        for period in self.periods:
            try:
                yield period, nesteddicts.get(self.content, [period] + var_path)
            except MissingDataError:
                continue

    # TODO Check that this isn't trying to grab a list descendant
    def get_observation(self, var_id: VariableId, period: str, treat_missing_as_null: bool = False) -> Optional[Any]:
        """Get the value of a temporal variable for a particular observation period."""
        var = self.as_var(var_id, track_type=TrackType.TEMPORAL)
        var_path: List = list(var.absolute_path)
        try:
            return nesteddicts.get(self.content, [period] + var_path)
        except MissingDataError as e:
            if treat_missing_as_null:
                return None
            raise e

    def put_immutable(self, var_id: VariableId, value: Optional[Any]) -> None:
        var = self.as_var(var_id, track_type=TrackType.IMMUTABLE)
        path: List = ["immutable"] + list(var.absolute_path)
        nesteddicts.put(self.content, path, value)

    def put_observation(self, var_id: VariableId, period: str, value: Optional[Any]) -> None:
        """Assign (or overwrite) the value of a temporal variable into a particular time period's observation."""
        var = self.as_var(var_id, track_type=TrackType.TEMPORAL)
        path: List = [period] + list(var.absolute_path)
        nesteddicts.put(self.content, path, value)

    def pop_observation(self, var_id: VariableId, period: str, treat_missing_as_null: bool = False) -> Optional[Any]:
        value: Optional[Any] = self.get_observation(var_id, period, treat_missing_as_null=treat_missing_as_null)
        self.del_observation(var_id, period)
        return value

    def del_observation(self, var_id: VariableId, period: str) -> None:
        var = self.as_var(var_id, track_type=TrackType.TEMPORAL)
        path: List = [period] + list(var.absolute_path)
        nesteddicts.delete(self.content, path)

    def del_immutable(self, var_id: VariableId) -> None:
        var = self.as_var(var_id, track_type=TrackType.IMMUTABLE)
        path: List = ["immutable"] + list(var.absolute_path)
        nesteddicts.delete(self.content, path)

    def encode_list(self, mappings: Dict[str, VariableId], content: List[Dict]) -> Iterator[Dict]:
        """Create a schema-compliant version of a list of dicts based on data structured in some other format.
        :param mappings: A mapping between the internal list item names and the IDs of the list-item variables they
        correspond to.
        :param content: The content in the internal format."""
        for list_item in content:
            ret: Dict = {}
            for internal_key in list_item.keys():
                if internal_key not in mappings:
                    raise ValueError('No mapping specified from internal key "%s" to schema' % internal_key)
                var_id: VariableId = mappings[internal_key]
                var: Variable = self.schema.get(var_id)
                path: List[str] = list(var.relative_path)
                nesteddicts.put(ret, path, list_item[internal_key])
            yield ret

    def decode_list(self, mappings: Dict[VariableId, str], content: List) -> Iterator[Dict]:
        """Convert a schema-compliant version of a list of dicts into some other format.
        :param mappings: A mapping between the variables and their string values.
        :param content: The content in the schema format.
        """
        path_mappings: Dict[VariableId, List[str]] = {}
        for var_id in mappings.keys():
            var: Variable = self.schema.get(var_id)
            if var is None:
                raise ValueError('Unrecognized variable ID "%s"' % var_id)
            path_mappings[var_id] = list(var.relative_path)

        for list_item in content:
            ret = {}
            for var_id, path in path_mappings.items():
                try:
                    value = nesteddicts.get(list_item, path)
                except MissingDataError:
                    continue
                internal_key = mappings[var_id]
                ret[internal_key] = value
            yield ret

    def encode_keyed_list(self, mappings: Dict[str, VariableId], content: Dict[str, Dict]) -> Dict:
        """Create a schema-compliant version of a keyed_list list of dicts based on data structured in some other format.
        :param mappings: A mapping between the internal list item names and the IDs of the list-item variables they
        correspond to.
        :param content: The content in the internal format."""
        ret = {}
        for key, list_item in content.items():
            encoded: Dict = {}
            for internal_key in list_item.keys():
                if internal_key not in mappings:
                    raise ValueError('No mapping specified from internal key "%s" to schema' % internal_key)
                var_id: VariableId = mappings[internal_key]
                var: Variable = self.schema.get(var_id)
                path: List[str] = list(var.relative_path)
                nesteddicts.put(encoded, path, list_item[internal_key])
            ret[key] = encoded
        return ret

    def decode_keyed_list(self, mappings: Dict[VariableId, str], content: Dict) -> Dict:
        """Convert a schema-compliant version of a keyed list of dicts into some other format.
        :param mappings: A mapping between the variables and their string values.
        :param content: The content in the schema format.
        """
        path_mappings: Dict[VariableId, List[str]] = {}
        for var_id in mappings.keys():
            var: Variable = self.schema.get(var_id)
            if var is None:
                raise ValueError('Unrecognized variable ID "%s"' % var_id)
            path_mappings[var_id] = list(var.relative_path)

        ret: Dict = {}
        for key, list_item in content.items():
            decoded = {}
            for var_id, path in path_mappings.items():
                try:
                    value = nesteddicts.get(list_item, path)
                except MissingDataError:
                    continue
                internal_key = mappings[var_id]
                decoded[internal_key] = value
            ret[key] = decoded
        return ret

    def __copy__(self) -> "Composite":
        # noinspection PyTypeChecker
        return self.__class__(self.schema, copy.deepcopy(self.content), composite_id=self.composite_id)

    def __deepcopy__(self) -> "Composite":
        return self.__copy__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Composite):
            return False
        if other.schema != self.schema:
            return False
        if other.composite_id != self.composite_id:
            return False
        if other.content != self.content:
            return False
        return True