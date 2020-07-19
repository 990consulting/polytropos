import json
import os
from typing import List, Dict, Optional, Type, Iterator, TYPE_CHECKING

from polytropos.actions.evolve import Change
from polytropos.actions.evolve.__lookup import load_lookups
from polytropos.util.loader import load

if TYPE_CHECKING:
    from polytropos.ontology.context import Context
    from polytropos.ontology.schema import Schema
    from polytropos.actions.evolve.__evolve import Evolve

class _EvolveFactory:
    def __init__(self, context: "Context",
                 change_specs: List[Dict],
                 schema: "Schema",
                 requested_lookups: Optional[List[str]]):

        self.change_classes: Dict[str, Type] = load(Change)
        self.requested_lookups: List[str] = requested_lookups or []
        self.change_specs: List[Dict] = change_specs
        self.schema: "Schema" = schema
        self.context: "Context" = context

    def _load_lookups(self) -> Dict[str, Dict]:
        return load_lookups(self.requested_lookups, self.context.lookups_dir)

    def _construct_change(self, class_name: str, mappings: Dict[str, str], loaded_lookups: Dict[str, Dict]) -> Change:
        change_class: Type = self.change_classes[class_name]
        change: Change = change_class(
            **mappings, schema=self.schema, lookups=loaded_lookups
        )
        return change

    def _construct_changes(self, loaded_lookups: Dict[str, Dict]) -> Iterator[Change]:
        for spec in self.change_specs:
            assert len(spec) == 1, "Malformed change specification"
            for class_name, var_specs in spec.items():
                change: Change = self._construct_change(class_name, var_specs, loaded_lookups)
                yield change

    def __call__(self, cls: Type) -> "Evolve":
        loaded_lookups: Dict[str, Dict] = self._load_lookups()
        change_instances: List[Change] = list(self._construct_changes(loaded_lookups))
        return cls(self.context, change_instances, self.schema)