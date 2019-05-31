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
        ('6_tr_export', 'custom_consumer', ''),
        ('6_tr_export', 'export_invariant_to_csv', ''),
        ('6_tr_export', 'export_temporal_to_csv', ''),
        ('6_tr_export', 'export_to_json', ''),
    ]
)
def test_task(scenario, task_name, expected_location):
    task = Task.build(scenario, task_name)
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
