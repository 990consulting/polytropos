from collections.abc import Callable
from difflib import Differ
import json
import os

import pytest
from polytropos.ontology.task import Task
from polytropos.util.compare import compare

@pytest.fixture
def basepath() -> str:
    return os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def run_task(basepath) -> Callable:
    def _run_task(scenario, task_name, expected_location):
        conf = os.path.join(basepath, '../../examples', scenario, 'conf')
        data = os.path.join(basepath, '../../examples', scenario, 'data')
        task = Task.build(conf, data, task_name)
        task.run()
        actual_path = os.path.join(
            task.path_locator.entities_dir, task.target_data
        )
        expected_path = os.path.join(
            task.path_locator.entities_dir, expected_location
        )
        assert os.listdir(actual_path) == os.listdir(expected_path)
        for filename in os.listdir(actual_path):
            with open(os.path.join(actual_path, filename), 'r') as f:
                with open(os.path.join(expected_path, filename), 'r') as g:
                    actual_data = json.load(f)
                    expected_data = json.load(g)
                    diff = Differ().compare(
                        json.dumps(actual_data, indent=4).split('\n'),
                        json.dumps(expected_data, indent=4).split('\n')
                    )
                    assert compare(actual_data, expected_data), (
                            'Diff: ' + '\n'.join(line for line in diff)
                    )
    return _run_task
