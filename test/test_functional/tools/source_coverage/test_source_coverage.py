import csv
from typing import Callable

import pytest
import random
import string
import os

from polytropos.actions.consume.source_coverage import SourceCoverage
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema

MODULE_BASEPATH: str = os.path.dirname(os.path.abspath(__file__))

random_slug: str = ''.join([random.choice(string.ascii_letters) for _ in range(10)])
output_path_template: str = "/tmp/source_cvg_{}_%s" % random_slug

@pytest.fixture(scope="module")
def do_run(source_schema: Callable, target_schema: Callable) -> Callable:
    def _do_run(data_type: str, output_dir: str) -> None:
        source: Schema = source_schema(data_type)
        target: Schema = target_schema(source, data_type)
        translate_dir: str = os.path.join(MODULE_BASEPATH, "fixtures", data_type, "translate")
        trace_dir: str = os.path.join(MODULE_BASEPATH, "fixtures", data_type, "trace")

        with Context.build(conf_dir="/tmp/dummy", data_dir="/tmp/dummy", output_dir=output_dir) as context:
            coverage: SourceCoverage = SourceCoverage(context, target, translate_dir, trace_dir)
            coverage("/tmp/dummy", "/tmp/dummy")

    return _do_run

@pytest.fixture(scope="module", autouse=True)
def setup(do_run) -> None:
    output_dir: str = output_path_template.format("text")
    os.mkdir(output_dir)
    do_run("Text", output_dir)

    # yield
    # shutil.rmtree(output_dir)

@pytest.mark.parametrize("case", ["Text"])
def test_cases(case):
    expected_path: str = os.path.join(MODULE_BASEPATH, "fixtures", case, "source_coverage.csv")
    actual_path: str = os.path.join(output_path_template.format(case), "source_coverage.csv")
    with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
        expected: csv.DictReader = csv.DictReader(expected_fh)
        actual: csv.DictReader = csv.DictReader(actual_fh)
        e_rows = [row for row in expected]
        a_rows = [row for row in actual]
        assert a_rows == e_rows
