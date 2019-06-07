import pytest
from difflib import Differ
import json
import os
from etl4.ontology.task import Task
from etl4.util.compare import compare


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
    conf = os.path.join('fixtures', scenario, 'conf')
    data = os.path.join('fixtures', scenario, 'data')
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


@pytest.mark.parametrize(
    'scenario,task_name,expected_location',
    [
        ('6_tr_export', 'custom_consumer', 'expected'),
        ('6_tr_export', 'export_invariant_to_csv', 'expected'),
        ('6_tr_export', 'export_temporal_to_csv', 'expected'),
        ('6_tr_export', 'export_to_json', 'expected'),
    ]
)
def test_task_consume(scenario, task_name, expected_location):
    conf = os.path.join('fixtures', scenario, 'conf')
    data = os.path.join('fixtures', scenario, 'data')
    task = Task.build(conf, data, task_name)
    task.run()
    actual_path = os.path.join(task.path_locator.conf_dir, '../')
    expected_path = os.path.join(
        task.path_locator.conf_dir, '../', expected_location
    )
    filename = task.steps[-1].filename
    with open(os.path.join(actual_path, filename), 'r') as f:
        with open(os.path.join(expected_path, filename), 'r') as g:
            actual_data = f.read()
            expected_data = g.read()
            assert actual_data == expected_data
