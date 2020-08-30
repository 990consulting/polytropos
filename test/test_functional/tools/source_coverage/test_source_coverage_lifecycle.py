import csv
import shutil
from typing import Callable

import pytest
import random
import string
import os

from polytropos.actions.consume.sourcecoverage import SourceCoverage
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

MODULE_BASEPATH: str = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture()
def output_dir() -> str:
    random_slug: str = ''.join([random.choice(string.ascii_letters) for _ in range(10)])
    dir_name: str = "/tmp/{}".format(random_slug)
    os.makedirs(dir_name)

    yield dir_name

    shutil.rmtree(dir_name)

@pytest.fixture()
def do_run(source_schema: Callable, target_schema: Callable) -> Callable:
    def _do_run(case: str, data_type: str, output_dir: str) -> None:
        source: Schema = source_schema(data_type)
        target: Schema = target_schema(source, data_type)
        translate_dir: str = os.path.join(MODULE_BASEPATH, "fixtures", case, "translate")
        trace_dir: str = os.path.join(MODULE_BASEPATH, "fixtures", case, "trace")

        with Context.build(conf_dir="/tmp/dummy", data_dir="/tmp/dummy", output_dir=output_dir) as context:
            coverage: SourceCoverage = SourceCoverage(context, target, translate_dir, trace_dir)
            coverage("/tmp/dummy", "/tmp/dummy")

    return _do_run

@pytest.fixture()
def do_test(do_run, output_dir) -> Callable:
    def _do_test(case: str, data_type: str) -> None:
        do_run(case, data_type, output_dir)
        expected_path: str = os.path.join(MODULE_BASEPATH, "fixtures", case, "source_coverage.csv")
        actual_path: str = os.path.join(output_dir, "source_coverage.csv")
        with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
            expected: csv.DictReader = csv.DictReader(expected_fh)
            actual: csv.DictReader = csv.DictReader(actual_fh)
            for a, e in zip(actual, expected):
                assert a == e
    return _do_test

def test_text_no_trivial(do_test):
    do_test("text_no_trivial", "Text")