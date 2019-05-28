import os
import yaml
import json
from etl4.ontology.metamorphosis import Metamorphosis
from etl4.ontology.schema import Schema
from etl4.ontology.task.__paths import TASKS_DIR, DATA_DIR


STEP_TYPES = {
    'Metamorphosis': Metamorphosis
}


class Task:
    def __init__(
        self,
        origin_data, origin_schema,
        target_data, target_schema=None
    ):
        self.origin_data = origin_data
        self.origin_schema = origin_schema
        self.target_data = target_data
        self.target_schema = target_schema
        self.steps = []

    @classmethod
    def build(cls, name):
        with open(os.path.join(TASKS_DIR, name + '.yaml'), 'r') as f:
            spec = yaml.safe_load(f)
        task = cls(
            origin_data=spec['starting_with']['data'],
            origin_schema=Schema.load(spec['starting_with']['schema']),
            target_data=spec['resulting_in']['data'],
            target_schema=Schema.load(spec['resulting_in'].get('schema'))
        )
        task.load_steps(spec['steps'])
        return task

    def load_steps(self, step_descriptions):
        for step in step_descriptions:
            # expect only one key/value pair
            assert len(step) == 1, (
                'Step description can have only one key, value pair'
            )
            for cls, kwargs in step.items():
                step_instance = STEP_TYPES[cls].build(
                    schema=self.origin_schema, **kwargs
                )
                self.steps.append(step_instance)

    def run(self):
        origin_path = os.path.join(DATA_DIR, self.origin_data)
        actual_path = os.path.join(DATA_DIR, self.target_data)
        try:
            os.mkdir(actual_path)
        except FileExistsError:
            pass
        for filename in os.listdir(origin_path):
            with open(os.path.join(origin_path, filename), 'r') as origin:
                data = json.load(origin)
                for step in self.steps:
                    step(data)
            with open(os.path.join(actual_path, filename), 'w') as target:
                json.dump(data, target)
