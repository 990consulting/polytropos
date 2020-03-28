from collections.abc import Callable
from difflib import Differ
import json
import os
from typing import List, Optional

import pytest

from polytropos.ontology.context import Context
from polytropos.ontology.task import Task
from polytropos.util.compare import compare
import polytropos.actions
from polytropos.util.paths import find_all_composites, relpath_for

@pytest.fixture
def run_task(basepath) -> Callable:
    # noinspection DuplicatedCode
    def _run_task(scenario, task_name, expected_location, output_dir: Optional[str] = None):
        polytropos.actions.register_all()
        conf = os.path.join(basepath, '../examples', scenario, 'conf')
        data = os.path.join(basepath, '../examples', scenario, 'data')
        with Context.build(conf, data, output_dir=output_dir) as context:
            task = Task.build(context, task_name)
            task.run()
        actual_path = os.path.join(
            task.context.entities_output_dir, task.target_data
        )
        expected_path = os.path.join(
            task.context.entities_input_dir, expected_location
        )
        composite_ids: List = list(find_all_composites(expected_path))
        assert sorted(find_all_composites(actual_path)) == sorted(composite_ids)
        for composite_id in composite_ids:
            relpath: str = relpath_for(composite_id)
            with open(os.path.join(actual_path, relpath, "%s.json" % composite_id)) as f:
                with open(os.path.join(expected_path, relpath, "%s.json" % composite_id)) as g:
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
