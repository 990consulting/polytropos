import csv
import os
import tempfile
from collections.abc import Callable

import pytest
from polytropos.ontology.schema import Schema

from polytropos.tools.schema.catalog import write_catalog

@pytest.fixture
def do_test(basepath: str) -> Callable:
    def _do_test(schema: Schema, expected_fn: str):
        expected_path: str = os.path.join(basepath, 'test_functional', 'tools', 'catalog', expected_fn)
        output_file: tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(mode="w", delete=False)
        write_catalog(schema, output_file)
        output_file.close()

        with open(output_file.name) as actual_fh, open(expected_path) as expected_fh:
            actual_reader: csv.reader = csv.reader(actual_fh)
            expected_reader: csv.reader = csv.reader(expected_fh)
            actual = [line for line in actual_reader]
            expected = [line for line in expected_reader]
        os.remove(output_file.name)
        assert actual == expected
    return _do_test

def test_source_catalog(source_schema, do_test):
    do_test(source_schema, "source_catalog.csv")

def test_target_catalog(target_schema, do_test):
    do_test(target_schema, "target_catalog.csv")
