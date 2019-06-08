import pytest
from difflib import Differ
import json
import os
from polytropos.ontology.task import Task
from polytropos.util.compare import compare

BASEPATH = os.path.dirname(os.path.abspath(__file__))

@pytest.mark.parametrize(
    'scenario,task_name,expected_location',
    [
        ('1_mm_only', 'infer_about_person', 'person/expected'),
        ('2_mm_scan', 'bmi_rank', 'person/expected'),
        ('3_mm_aggregate_mm_scan', 'economy', 'city/expected'),
        ('4_filter_mm_scan', 'bmi_rank', 'person/expected'),
    ]
)
def test_task(scenario, task_name, expected_location):
    conf = os.path.join(BASEPATH, '../../../fixtures', scenario, 'conf')
    data = os.path.join(BASEPATH, '../../../fixtures', scenario, 'data')
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


