from collections import Callable
from typing import Tuple

import pytest
import os
from polytropos.ontology.task import Task
import polytropos.actions
import json

BASEPATH = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope='module', autouse=True)
def cleanup():
    # Setup -- runs before tests begin
    def delete_if_exists(filename):
        path = (BASEPATH + "../../examples/5_tr_export/" + filename)
        if os.path.exists(path):
            os.remove(path)

    yield  # Idiomatic pytest (i.e., a hack) to have custom setup and teardown

    # Teardown -- runs after tests finish
    delete_if_exists("count_output.txt")
    delete_if_exists("immutable.csv")
    delete_if_exists("temporal.csv")
    delete_if_exists("records.json")

@pytest.fixture()
def do_export() -> Callable:
    def _do_export(task_name: str) -> Tuple[str, str]:
        polytropos.actions.register_all()
        conf = os.path.join(BASEPATH, '../../examples', "s_5_tr_export", 'conf')
        data = os.path.join(BASEPATH, '../../examples', "s_5_tr_export", 'data')
        task = Task.build(conf, data, task_name)
        task.run()
        actual_path: str = os.path.join(task.path_locator.conf_dir, '../')
        expected_path: str = os.path.join(
            task.path_locator.conf_dir, '../', "expected"
        )
        filename: str = task.steps[-1].filename
        actual_fn: str = os.path.join(actual_path, filename)
        expected_fn: str = os.path.join(expected_path, filename)
        return actual_fn, expected_fn
    return _do_export

def test_task_json_exporter(do_export):
    actual_fn, expected_fn = do_export("export_to_json")
    with open(actual_fn) as actual_fh, open(expected_fn) as expected_fh:
        actual = json.load(actual_fh)
        expected = json.load(expected_fh)
        assert actual == expected

def test_task_custom_consumer(do_export):
    import examples.s_5_tr_export.conf.consumers.count
    actual_fn, expected_fn = do_export("custom_consumer")
    with open(actual_fn) as actual_fh, open(expected_fn) as expected_fh:
        actual = actual_fh.read()
        expected = expected_fh.read()
        assert actual == expected
