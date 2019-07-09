import os
import tempfile

import pytest

from polytropos.cli.linkage import ExportLinkages, ImportLinkages
import csv

from polytropos.ontology.variable import Variable

def test_export_linkages(target_schema, basepath):
    """Export the schema as it exists in the fixture and verify that it meets the expected format."""
    expected_path: str = os.path.join(basepath, 'test_functional', 'cli', 'linkages', 'unmodified_linkages.csv')
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

@pytest.mark.parametrize("target_id, source_ids", [
    ("target_t_folder", None),
    ("target_t_folder_text", ["source_t_folder_text_1", "source_t_folder_text_2"]),
    ("target_t_list", ["source_t_list_1", "source_t_list_2"]),
    ("target_t_list_text", ["source_t_list_text_1", "source_t_list_text_2"]),
    ("target_t_named_list", ["source_t_named_list_1", "source_t_named_list_2"]),
    ("target_t_named_list_text", ["source_t_named_list_text_1", "source_t_named_list_text_2"]),
    ("target_i_folder", None),
    ("target_i_folder_text", None),
    ("target_i_list", ["source_i_list_2"]),
    ("target_i_list_text", ["source_i_list_text_2"]),
    ("target_i_named_list", ["source_i_named_list_2"]),
    ("target_i_named_list_text", ["source_i_named_list_text_2"])
])
def test_import_modifications(target_schema, basepath, target_id, source_ids):
    """Apply the modified linkage file to the schema, then verify that the sources are as expected."""
    mods_path: str = os.path.join(basepath, 'test_functional', 'cli', 'linkages', 'modified_linkages.csv')
    with open(mods_path) as fh:
        do_import: ImportLinkages = ImportLinkages(target_schema, fh)
        do_import()
    var: Variable = target_schema.get(target_id)
    assert var.sources == source_ids

#def test_lifecycle():
#    """Apply the modified linkage file to the schema, export the linkages of the modified schema, and verify that the
#    export matches the modified linkage file."""
#    pytest.fail()
