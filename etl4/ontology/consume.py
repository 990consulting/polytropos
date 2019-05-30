from collections.abc import Callable
from abc import abstractmethod
from dataclasses import dataclass
from typing import Tuple, Dict, Iterable
from etl4.ontology.step import Step
from etl4.ontology.task.__loader import load


# TODO Quimey, unlike the other tasks, consumers may take arguments that are not variables. We may want the ability to
#  do this in general--for example, if a task does a statistical analysis and we want to provide some tuning parameter.
#  I'm not sure if this actually creates a problem or not.
class Consume(Step):
    """Export data from a set of composites to a single file."""
    @classmethod
    def build(cls, path_locator, schema, name):
        consumes = load(
            path_locator.consumes_dir, path_locator.consumes_import, cls
        )
        return consumes[name]()

    def before(self):
        """Optional actions to be performed after the constructor runs but before starting to consume composites."""
        pass

    def after(self):
        """Optional actions to be performed after the composites are all consumed."""

    @abstractmethod
    def consume(self, composite_id: str, composite: Dict):
        pass

    def __call__(self, origin, target):
        """Generate the export file."""
        self.before()
        for filename in os.listdir(origin):
            with open(os.path.join(origin, filename), 'r') as origin_file:
                composite = json.load(origin_file)
                self.consume(filename, composite)
        self.after()
