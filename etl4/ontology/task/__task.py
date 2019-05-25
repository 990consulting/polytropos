from dataclasses import dataclass, field
from typing import List, Any, TypeVar, Dict
import os
import yaml
import json
import dacite
from etl4.ontology.metamorphosis import Metamorphosis


TASKS_DIR = 'fixtures/conf/tasks'
DATA_DIR = 'fixtures/data'
STEP_TYPES = {
    'Metamorphosis': Metamorphosis
}


@dataclass
class StartingWith:
    data: str
    schema: str

@dataclass
class ResultingIn:
    data: str


@dataclass
class Task:
    starting_with: StartingWith
    resulting_in: ResultingIn
    step_descriptions: List
    steps: List = field(default_factory=list, init=False)

    @classmethod
    def build(cls, name):
        with open(os.path.join(TASKS_DIR, name + '.yaml'), 'r') as f:
            spec = yaml.safe_load(f)
        # dirty trick
        spec['step_descriptions'] = spec['steps']
        del spec['steps']
        task = dacite.from_dict(data_class=cls, data=spec)
        task.load_starting_with()
        task.load_steps()
        return task

    def load_starting_with(self):
        pass

    def load_steps(self):
        for step in self.step_descriptions:
            # expect only one key/value pair
            for cls, kwargs in step.items():
                step_instance = STEP_TYPES[cls].build(
                    schema=self.starting_with.schema, **kwargs
                )
                self.steps.append(step_instance)

    def run(self):
        try:
            os.mkdir(os.path.join(DATA_DIR, self.resulting_in.data))
        except FileExistsError:
            pass
        for filename in os.listdir(
                os.path.join(DATA_DIR, self.starting_with.data)
        ):
            with open(
                    os.path.join(DATA_DIR, self.resulting_in.data, filename),
                    'w'
            ) as f:
                json.dump({}, f)
