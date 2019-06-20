import json
import logging
import os
from difflib import Differ

from polytropos.ontology.task import Task
from polytropos.util.compare import compare

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

BASEPATH = os.path.dirname(os.path.abspath(__file__))
def run_task(scenario, task_name, expected_location):
    conf = os.path.join(BASEPATH, '../examples', scenario, 'conf')
    data = os.path.join(BASEPATH, '../examples', scenario, 'data')
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

import examples.s_1_mm_only.conf.changes.vitals
import examples.s_1_mm_only.conf.changes.description
import examples.s_1_mm_only.conf.changes.color
run_task('s_1_mm_only', 'infer_about_person', 'person/expected')
