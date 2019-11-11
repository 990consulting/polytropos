from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Callable, List, Any, cast

from polytropos.ontology.composite import Composite

from polytropos.actions.evolve import Change
from polytropos.ontology.variable import VariableId, Variable, Primitive
from polytropos.util.nesteddicts import MissingDataError
from polytropos.util import nesteddicts

@dataclass  # type: ignore
class UniversalChange(Change, ABC):
    source: VariableId
    target: VariableId
    list_base: Optional[VariableId] = field(default=None)

    def __post_init__(self) -> None:
        var: Variable = self.schema.get(self.source)

        self.temporal = var.temporal

        act_options: Dict[str, Callable] = {
            "List": self._list,
            "KeyedList": self._keyed_list
        }

        if self.list_base:
            self._act = act_options[self.schema.get(self.list_base).data_type]
            self._list_base_path: List[str] = self.schema.get(self.list_base).absolute_path
        else:
            self._act = self._single

        self.source_path: List[str] = self.schema.get(self.source).relative_path
        self.target_path: List[str] = self.schema.get(self.target).relative_path

    def _list(self, content: Dict) -> None:
        try:
            source_list: List[Dict] = nesteddicts.get(content, self._list_base_path)
            for entry in source_list:
                self._single(entry)
        except MissingDataError:
            return

    def _keyed_list(self, content: Dict) -> None:
        try:
            source_klist: Dict[str, Dict] = nesteddicts.get(content, self._list_base_path)
            for entry in source_klist.values():
                self._single(entry)
        except MissingDataError:
            return

    @abstractmethod
    def _single(self, content: Dict) -> None:
        pass

    def __call__(self, composite: Composite) -> None:
        if self.temporal:
            for period in composite.periods:
                content: Dict = composite.content[period]
                self._act(content)
        else:
            if "immutable" not in composite.content:
                return
            content = composite.content["immutable"]
            self._act(content)
