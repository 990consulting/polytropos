import os
from shutil import rmtree
import yaml
from tempfile import TemporaryDirectory
from etl4.ontology.metamorphosis import Metamorphosis
from etl4.ontology.scan import Scan
from etl4.ontology.filter import Filter
from etl4.ontology.aggregation import Aggregation
from etl4.ontology.schema import Schema
from etl4.ontology.task.__paths import TaskPathLocator


STEP_TYPES = {
    'Metamorphosis': Metamorphosis,
    'Scan': Scan,
    'Aggregation': Aggregation,
    'Filter': Filter
}


class Task:
    def __init__(
        self, path_locator,
        origin_data, origin_schema,
        target_data, target_schema=None
    ):
        self.path_locator = path_locator
        self.origin_data = origin_data
        self.origin_schema = origin_schema
        self.target_data = target_data
        self.target_schema = target_schema
        self.steps = []

    @classmethod
    def build(cls, scenario, name):
        path_locator = TaskPathLocator(scenario)
        with open(
                os.path.join(path_locator.tasks_dir, name + '.yaml'), 'r'
        ) as f:
            spec = yaml.safe_load(f)
        task = cls(
            path_locator=path_locator,
            origin_data=spec['starting_with']['data'],
            origin_schema=Schema.load(
                path_locator, spec['starting_with']['schema']
            ),
            target_data=spec['resulting_in']['data'],
            target_schema=Schema.load(
                path_locator, spec['resulting_in'].get('schema')
            )
        )
        task.load_steps(spec['steps'])
        return task

    def load_steps(self, step_descriptions):
        current_schema = self.origin_schema
        for step in step_descriptions:
            # expect only one key/value pair
            assert len(step) == 1, (
                'Step description can have only one key, value pair'
            )
            for cls, kwargs in step.items():
                step_instance = STEP_TYPES[cls].build(
                    path_locator=self.path_locator, schema=current_schema, **kwargs
                )
                self.steps.append(step_instance)
                if cls == 'Aggregation':
                    current_schema = step_instance.target_schema

    def run(self):
        origin_path = os.path.join(self.path_locator.entities_dir, self.origin_data)
        actual_path = os.path.join(self.path_locator.entities_dir, self.target_data)
        try:
            rmtree(actual_path)
        except FileNotFoundError:
            pass
        os.mkdir(actual_path)
        current_path = origin_path
        current_path_obj = None
        next_path = None
        for step in self.steps:
            next_path = TemporaryDirectory(dir=self.path_locator.data_dir)
            step(current_path, next_path.name)
            if current_path_obj:
                current_path_obj.cleanup()
            current_path = next_path.name
            current_path_obj = next_path
        os.rename(next_path.name, actual_path)
        os.mkdir(next_path.name)
        next_path.cleanup()
