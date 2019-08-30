import os
from typing import Callable, Tuple, Dict, List

import pytest
import yaml

from polytropos.actions.consume.tocsv.descriptors.colnames import DescriptorBlockToColumnNames
from polytropos.actions.consume.tocsv.descriptors.fromraw import GetAllColumnNames

@pytest.fixture()
def all_column_names(schema) -> GetAllColumnNames:
    spec_to_names: DescriptorBlockToColumnNames = DescriptorBlockToColumnNames(schema)
    return GetAllColumnNames(spec_to_names)

@pytest.fixture()
def do_test(all_column_names, basepath) -> Callable:
    task_dir: str = os.path.join(basepath, "..", "examples", "s_7_csv", "conf", "tasks")

    def _do_test(filename: str, expected: Tuple) -> None:
        task_path: str = os.path.join(task_dir, filename)
        with open(task_path) as fh:
            task_spec: Dict = yaml.full_load(fh)
        column_spec: List = task_spec["steps"][0]["Consume"]["columns"]
        actual: Tuple = all_column_names(column_spec)
        assert actual == expected
    return _do_test

def test_immutable_singleton(do_test):
    filename: str = "01_immutable_singleton.yaml"
    expected: Tuple = ("id", "/i_folder/some_text")
    do_test(filename, expected)

def test_immutable_singleton_custom_name(do_test):
    filename: str = "03_immutable_singleton_custom_name.yaml"
    expected: Tuple = ("id", "custom_name")
    do_test(filename, expected)

def test_immutable_and_temporal_singletons(do_test):
    filename: str = "04_immutable_and_temporal_singletons.yaml"
    expected: Tuple = ("id", "period", "/i_folder/some_text", "/t_folder/some_text")
    do_test(filename, expected)

def test_temporal_list_and_immutable_named_list(do_test):
    filename: str = "05_temporal_list_and_immutable_named_list.yaml"
    expected: Tuple = ("id", "period", "/t_list/some_text", "/simple_named_list", "special name")
    do_test(filename, expected)
