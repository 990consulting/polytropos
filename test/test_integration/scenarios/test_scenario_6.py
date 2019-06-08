import pytest
import os
from polytropos.ontology.task import Task

BASEPATH = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope='module', autouse=True)
def cleanup():
    # Setup -- runs before tests begin
    def delete_if_exists(filename):
        path = (BASEPATH + "/../../../fixtures/6_tr_export/" + filename)
        if os.path.exists(path):
            os.remove(path)

    yield  # Idiomatic pytest (i.e., a hack) to have custom setup and teardown

    # Teardown -- runs after tests finish
    delete_if_exists("count_output.txt")
    delete_if_exists("immutable.csv")
    delete_if_exists("temporal.csv")
    delete_if_exists("records.json")

@pytest.mark.parametrize(
    'scenario,task_name,expected_location',
    [
        ('6_tr_export', 'custom_consumer', 'expected'),
        ('6_tr_export', 'export_immutable_to_csv', 'expected'),
        ('6_tr_export', 'export_temporal_to_csv', 'expected'),
        ('6_tr_export', 'export_to_json', 'expected'),
    ]
)
def test_task_consume(scenario, task_name, expected_location):
    conf = os.path.join(BASEPATH, '../../../fixtures', scenario, 'conf')
    data = os.path.join(BASEPATH, '../../../fixtures', scenario, 'data')
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
