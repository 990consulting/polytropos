from dataclasses import dataclass
from typing import Dict, Iterator, Optional, Any, Tuple, List

from polytropos.util.nesteddicts import MissingDataError

from polytropos.util import nesteddicts

from polytropos.ontology.schema import Schema, TrackType
from polytropos.ontology.variable import Variable

@dataclass
class Composite:
    schema: Schema
    content: Dict

    def get_periods(self) -> Iterator[str]:
        """Iterate over all of the observation periods contained in this composite."""
        yield from set(self.content.keys()) - {"invariant"}

    # TODO Check that this isn't trying to grab a list descendant
    def get_immutable(self, var_id: str, treat_missing_as_null=False) -> Optional[Any]:
        """Get an immutable variable from this composite."""
        var: Variable = self.schema.get(var_id, track_type=TrackType.IMMUTABLE)
        path = ["immutable"] + list(var.absolute_path)
        return nesteddicts.get(self.content, path)

    # TODO Check that this isn't trying to grab a list descendant
    def get_all_observations(self, var_id: str) -> Iterator[Tuple[str, Any]]:
        """Iterate over all observations of a temporal variable from this composite."""
        var: Variable = self.schema.get(var_id, track_type=TrackType.TEMPORAL)
        var_path: List = list(var.absolute_path)
        for period in self.get_periods():
            try:
                yield period, nesteddicts.get(self.content, [period] + var_path)
            except MissingDataError:
                continue

    # TODO Check that this isn't trying to grab a list descendant
    def get_observation(self, var_id: str, period: str, treat_missing_as_null=False) -> Optional[Any]:
        """Get the value of a temporal variable for a particular observation period."""
        var: Variable = self.schema.get(var_id, track_type=TrackType.TEMPORAL)
        var_path: List = list(var.absolute_path)
        return nesteddicts.get(self.content, [period] + var_path, accept_none=treat_missing_as_null)

    def put_immutable(self, var_id: str, value: Optional[Any]) -> None:
        var: Variable = self.schema.get(var_id, track_type=TrackType.IMMUTABLE)
        path: List = ["immutable"] + list(var.absolute_path)
        nesteddicts.put(self.content, path, value)

    def put_observation(self, period: str, var_id: str, value: Optional[Any]) -> None:
        """Assign (or overwrite) the value of a temporal variable into a particular time period's observation."""
        pass

    def encode_list(self, mappings: Dict[str, str], content: List):
        """Create a schema-compliant version of a list of dicts based on data structured in some other format.
        :param mappings: A mapping between the internal list item names and the IDs of the list-item variables they
        correspond to.
        :param content: The content in the internal format."""
        pass

    def decode_list(self, mappings: Dict[Variable, str], content: List) -> Iterator[Dict]:
        """Convert a schema-compliant version of a list of dicts into some other format.
        :param mappings: A mapping between the variables and their string values.
        :param content: The content in the schema format.
        """
        pass

    def encode_named_list(self, mappings: Dict[str, str], content: Dict[str, Dict]):
        """Create a schema-compliant version of a named list of dicts based on data structured in some other format.
        :param mappings: A mapping between the internal list item names and the IDs of the list-item variables they
        correspond to.
        :param content: The content in the internal format."""
        pass

    def decode_named_list(self, mappings: Dict[Variable, str], content: List) -> Iterator[Dict]:
        """Convert a schema-compliant version of a named list of dicts into some other format.
        :param mappings: A mapping between the variables and their string values.
        :param content: The content in the schema format.
        """
        pass
