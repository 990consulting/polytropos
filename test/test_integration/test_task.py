import pytest
import json
import os
from etl4.ontology.task import Task


@pytest.mark.parametrize(
    'scenario,task_name',
    [
        ('1_mm_only', 'infer_about_person'),
        ('2_mm_scan', 'bmi_rank'),
        ('3_mm_aggregate_mm_scan', 'economy'),
        ('4_filter_mm_scan', 'bmi_rank'),
    ]
)
def test_task(scenario, task_name):
    task = Task.build(scenario, task_name)
    task.run()
    actual_path = os.path.join(
        task.path_locator.entities_dir, task.target_data
    )
    expected_path = os.path.join(
        task.path_locator.entities_dir, 'expected'
    )
    assert os.listdir(actual_path) == os.listdir(expected_path)
    for filename in os.listdir(actual_path):
        with open(os.path.join(actual_path, filename), 'r') as f:
            with open(os.path.join(expected_path, filename), 'r') as g:
                assert json.load(f) == json.load(g)
