import csv
import os
from typing import List

import polytropos.actions
import pytest
import shutil

import polytropos.actions
from polytropos.ontology.context import Context
from polytropos.ontology.task import Task

BASEPATH = os.path.dirname(os.path.abspath(__file__))
FIXTURE_PATH: str = os.path.join(BASEPATH, "..", "..", "examples", "s_7_csv")
WORKING_PATH: str = os.path.join("/tmp/polytropos_csv_test")


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    shutil.rmtree(WORKING_PATH, ignore_errors=True)
    polytropos.actions.register_all()
    data_dir: str = os.path.join(FIXTURE_PATH, "data")
    conf_dir: str = os.path.join(FIXTURE_PATH, "conf")
    task_dir: str = os.path.join(conf_dir, "tasks")
    with Context.build(conf_dir, data_dir, output_dir=WORKING_PATH) as context:
        for file in os.scandir(task_dir):
            task_name: str = file.name[:-5]
            task = Task.build(context, task_name)
            task.run()
    yield
    shutil.rmtree(WORKING_PATH, ignore_errors=True)

@pytest.mark.parametrize("filename", [
    "01_immutable_singleton.csv",
    "02_immutable_singleton_all_empty.csv",
    "03_immutable_singleton_custom_name.csv",
    "04_immutable_and_temporal_singletons.csv",
    "05_temporal_list_and_immutable_keyed_list.csv",
    "06_deep_nesting.csv",
    "07_temporal_singleton_filter.csv",
    "08_multitext.csv"
])
def test_all_fixtures(filename: str):
    actual_path: str = os.path.join(WORKING_PATH, filename)
    expected_path: str = os.path.join(FIXTURE_PATH, "expected", filename)
    with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
        # The exporter writes composites as they are processed, which means order is essentially random
        actual: List[List[str]] = sorted(line for line in csv.reader(actual_fh))
        expected: List[List[str]] = sorted(line for line in csv.reader(expected_fh))
    if actual != expected:
        print("breakpoint")
    assert actual == expected
