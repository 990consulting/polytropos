import json
import os
from dataclasses import dataclass, field
from typing import Optional, Any, Iterable, Tuple, TextIO

from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite

@dataclass
class ExportToJSON(Consume):
    filename: str
    indent: int = 2
    fobj: Optional[TextIO] = field(default=None, init=False)
    first: bool = field(default=True, init=False)

    def before(self) -> None:
        assert self.context is not None
        self.fobj = open(
            os.path.join(self.context.output_dir, self.filename), 'w'
        )
        self.fobj.write('{\n')

    def extract(self, composite: Composite) -> Optional[Any]:
        return composite

    def _to_json(self, composite_id: str, composite: Composite) -> None:
        assert self.fobj is not None
        if not self.first:
            self.fobj.write(',\n')
        self.first = False
        self.fobj.write(' ' * self.indent + f'"{composite_id}": ')
        data = json.dumps(composite.content, indent=self.indent).split('\n')
        for i, line in enumerate(data):
            if i:
                self.fobj.write('\n')
                self.fobj.write(' ' * self.indent)
            self.fobj.write(line)

    def consume(self, extracts: Iterable[Tuple[str, Composite]]) -> None:
        for composite_id, composite in extracts:  # type: str, Composite
            composite_id = composite_id
            self._to_json(composite_id, composite)

    def after(self) -> None:
        assert self.fobj is not None
        self.fobj.write('\n}')
        self.fobj.close()