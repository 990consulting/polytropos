import json
import os
from dataclasses import dataclass

from polytropos.actions.consume import Consume
from polytropos.ontology.composite import Composite

@dataclass
class ExportToJSON(Consume):
    filename: str
    indent: int = 2

    def __post_init__(self):
        self.fobj = None
        self.first = True

    def before(self):
        # noinspection PyAttributeOutsideInit
        self.fobj = open(
            os.path.join(self.path_locator.conf, '../', self.filename), 'w'
        )
        self.fobj.write('{\n')

    def consume(self, composite_id: str, composite: Composite):
        if not self.first:
            self.fobj.write(',\n')
        # noinspection PyAttributeOutsideInit
        self.first = False
        self.fobj.write(' ' * self.indent + f'"{composite_id}": ')
        data = json.dumps(composite.content, indent=self.indent).split('\n')
        for i, line in enumerate(data):
            if i:
                self.fobj.write('\n')
                self.fobj.write(' ' * self.indent)
            self.fobj.write(line)

    def after(self):
        self.fobj.write('\n}')
        self.fobj.close()