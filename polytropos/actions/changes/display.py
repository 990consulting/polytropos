from dataclasses import dataclass
from typing import Dict, cast, Callable, Optional, Any

from polytropos.util import nesteddicts

from polytropos.actions.changes.universal import UniversalChange
from polytropos.ontology.variable import Primitive

@dataclass
class DisplayFormat(UniversalChange):

    def __post_init__(self) -> None:
        super(DisplayFormat, self).__post_init__()
        var: Primitive = cast(Primitive, self.schema.get(self.source))  # type: ignore
        self.display_format: Callable = var.display_format  # type: ignore

    def _single(self, content: Dict) -> None:
        raw: Optional[Any] = nesteddicts.get(content, self.source_path, default=None)
        if raw is None:
            return
        display: str = self.display_format(raw)
        nesteddicts.put(content, self.target_path, display)
