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


