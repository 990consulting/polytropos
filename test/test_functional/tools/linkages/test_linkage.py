import os
import tempfile

import pytest

from polytropos.tools.schema.linkage import ExportLinkages
import csv

from polytropos.ontology.variable import Variable

def test_export_linkages(target_schema, basepath):
    """Export the schema as it exists in the fixture and verify that it meets the expected format."""
    expected_path: str = os.path.join(basepath, 'test_functional', 'tools', 'linkages', 'unmodified_linkages.csv')
    output_file: tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(mode="w", delete=False)
    export: ExportLinkages = ExportLinkages(target_schema, output_file)
    export()
    output_file.close()

    with open(output_file.name) as actual_fh, open(expected_path) as expected_fh:
        actual_reader: csv.reader = csv.reader(actual_fh)
        expected_reader: csv.reader = csv.reader(expected_fh)
        actual = [line for line in actual_reader]
        expected = [line for line in expected_reader]
    os.remove(output_file.name)
    assert actual == expected
