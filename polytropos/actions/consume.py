import os
import json
from abc import abstractmethod
from dataclasses import dataclass

from polytropos.ontology.composite import Composite

from polytropos.actions.step import Step
from polytropos.ontology.schema import Schema
from polytropos.util.loader import load
from polytropos.ontology.paths import PathLocator


@dataclass
class Consume(Step):
    path_locator: PathLocator
    schema: Schema

    """Export data from a set of composites to a single file."""
    @classmethod
    def build(cls, path_locator: PathLocator, schema: Schema, name: str, **kwargs):
        consumes = load(cls)
        return consumes[name](path_locator, schema, **kwargs)

    def before(self):
        """Optional actions to be performed after the constructor runs but before starting to consume composites."""
        pass

    def after(self):
        """Optional actions to be performed after the composites are all consumed."""

    @abstractmethod
    def consume(self, composite_id: str, composite: Composite):
        pass

    def __call__(self, origin_dir: str, target_dir: str):
        """Generate the export file."""
        self.before()
        for filename in sorted(os.listdir(origin_dir)):
            with open(os.path.join(origin_dir, filename), 'r') as origin_file:
                content = json.load(origin_file)
                composite: Composite = Composite(self.schema, content)
                self.consume(filename[:-5], composite)
        self.after()


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
