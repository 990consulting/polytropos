import os
import yaml


TASKS_DIR = 'fixtures/conf/tasks'


class Task:
    def __init__(self):
        pass

    @classmethod
    def build(name):
        with open(os.path.join(TASKS_DIR, name), 'r') as f:
            return yaml.load(f)
