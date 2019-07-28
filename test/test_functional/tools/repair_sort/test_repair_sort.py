import json
import os
import random
import shutil
import string
from typing import Callable, Dict

import pytest

from polytropos.tools.schema.repair_sort import repair_sort_order

@pytest.fixture(scope="module")
def module_basepath():
    return os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="module")
def output_basepath() -> str:
    dirname: str = ''.join([random.choice(string.ascii_letters) for n in range(10)])
    return "/tmp/%s" % dirname

@pytest.fixture(scope="module", autouse=True)
def setup(module_basepath: str, output_basepath: str):
    os.mkdir(output_basepath)
    schema_path: str = os.path.join(module_basepath, "schema")
    for file_name in os.listdir(schema_path):
        full_path: str = os.path.join(schema_path, file_name)
        shutil.copy(full_path, output_basepath)
    repair_sort_order(output_basepath)

    yield

    shutil.rmtree(output_basepath)

@pytest.fixture()
def do_test(module_basepath: str, output_basepath: str) -> Callable:
    def _do_test(track_name: str):
        fn: str = track_name + "_repaired.json"
        expected_fn: str = os.path.join(module_basepath, "expected", fn)
        actual_fn: str = os.path.join(output_basepath, fn)
        with open(actual_fn) as actual_fh, open(expected_fn) as expected_fh:
            actual: Dict = json.load(actual_fh)
            expected: Dict = json.load(expected_fh)
            assert actual == expected
    return _do_test

@pytest.mark.parametrize("track_name", ["temporal", "immutable"])
def test_repair_sort(do_test, track_name):
    do_test(track_name)
