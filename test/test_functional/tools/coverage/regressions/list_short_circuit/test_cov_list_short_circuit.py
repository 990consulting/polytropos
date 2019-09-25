"""Regression tests for previous bugs in coverage report"""
import csv
import os
import shutil
from typing import Dict

import pytest

from polytropos.actions.consume.coverage import CoverageFile
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

output_path: str = os.path.join("/tmp", "cov_list_short_circuit_test")

@pytest.fixture(autouse=True)
def cleanup() -> None:
    yield
    shutil.rmtree(output_path)

def test_nested_does_not_short_circuit_crawl():
    """Bug history:
         - Detected around 9/20/2019
         - Isolated minimum reproducible case on 9/24/2019
         - Caused by commit e23b825 (8/27/2019)
         - Regression test based on minimum reproducible case
    """
    spec: Dict = {
        "root": {
            "name": "return",
            "data_type": "Folder",
            "sort_order": 0
        },
        "application_submissions": {
            "name": "application_submissions",
            "data_type": "List",
            "parent": "root",
            "sort_order": 0
        },
        "award_restrict": {
            "name": "award_restrict",
            "data_type": "Text",
            "parent": "application_submissions",
            "sort_order": 0
        },
        "filer": {
            "name": "filer",
            "data_type": "Folder",
            "parent": "root",
            "sort_order": 1
        },
        "name_org": {
            "name": "name_org",
            "data_type": "Text",
            "parent": "filer",
            "sort_order": 0
        }
    }

    temporal: Track = Track.build(spec, None, "temporal")
    immutable: Track = Track.build({}, None, "immutable")
    schema: Schema = Schema(temporal, immutable, name="semantic")

    context: Context = Context.build(conf_dir="dummy", data_dir="dummy")
    basepath: str = os.path.dirname(os.path.abspath(__file__))
    composite_path: str = os.path.join(basepath, "data")

    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path)
    coverage: CoverageFile = CoverageFile(context, schema, output_path + "/semantic", None, None)
    coverage(composite_path, "dummy")

    expected_path: str = os.path.join(basepath, "expected.csv")
    actual_path: str = os.path.join(output_path, "semantic_temporal.csv")
    with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
        expected: csv.DictReader = csv.DictReader(expected_fh)
        actual: csv.DictReader = csv.DictReader(actual_fh)
        e_rows = [row for row in expected]
        a_rows = [row for row in actual]
        assert a_rows == e_rows
