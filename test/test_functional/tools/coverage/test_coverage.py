import csv
import os
import random
import shutil
import string
from typing import Callable, Optional, Dict
import pytest

from polytropos.actions.consume.coverage import CoverageFile
from polytropos.ontology.paths import PathLocator

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

# Same as the function-scoped one declared a couple levels up, but deals with scope mismatch issues
@pytest.fixture(scope="module")
def module_source_track(half_source_spec) -> Callable:
    def _track(prefix, track_name) -> Track:
        first_half: Dict = half_source_spec(1, "first", prefix, track_name)
        second_half: Dict = half_source_spec(2, "second", prefix, track_name)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track

# Same as the function-scoped one declared a couple levels up, but deals with scope mismatch issues
@pytest.fixture(scope="module")
def module_source_schema(module_source_track) -> Schema:
    temporal: Track = module_source_track("t", "temporal")
    immutable: Track = module_source_track("i", "immutable")
    return Schema(temporal, immutable)

@pytest.fixture(scope="module")
def module_basepath():
    return os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="module")
def path_locator() -> PathLocator:
    ret: PathLocator = PathLocator("dummy", "dummy")
    return ret

@pytest.fixture(scope="module")
def output_basepath() -> str:
    dirname: str = ''.join([random.choice(string.ascii_letters) for n in range(10)])
    return "/tmp/%s" % dirname


@pytest.fixture(scope="module")
def do_run(module_basepath: str, module_source_schema: Schema, path_locator, output_basepath) -> Callable:
    def _do_run(test_name: str, t_group_var: Optional[str], i_group_var: Optional[str]):
        composite_path: str = os.path.join(module_basepath, "composites")
        output_path: str = os.path.join(output_basepath, test_name + "/" + test_name)
        coverage: CoverageFile = CoverageFile(path_locator, module_source_schema, output_path, t_group_var, i_group_var)
        coverage(composite_path, "dummy")
    return _do_run

@pytest.fixture(scope="module", autouse=True)
def setup(do_run, output_basepath) -> None:
    os.mkdir(output_basepath)
    os.mkdir(os.path.join(output_basepath, "grouped"))
    os.mkdir(os.path.join(output_basepath, "ungrouped"))

    do_run("ungrouped", None, None)
    do_run("grouped", "source_t_folder_text_1", "source_i_folder_text_2")

    yield

    shutil.rmtree(output_basepath)

@pytest.mark.parametrize("filename", [
    "grouped/grouped_immutable.csv",
    "grouped/grouped_immutable_groups.csv",
    "grouped/grouped_temporal.csv",
    "grouped/grouped_temporal_groups.csv",
    "ungrouped/ungrouped_immutable.csv",
    "ungrouped/ungrouped_immutable_groups.csv",
    "ungrouped/ungrouped_temporal.csv",
    "ungrouped/ungrouped_temporal_groups.csv"
])
def test_files_match(module_basepath, output_basepath, filename):
    expected_path: str = os.path.join(module_basepath, "expected", filename)
    actual_path: str = os.path.join(output_basepath, filename)
    with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
        expected: csv.DictReader = csv.DictReader(expected_fh)
        actual: csv.DictReader = csv.DictReader(actual_fh)
        e_rows = [row for row in expected]
        a_rows = [row for row in actual]
        #for a_row, e_row in zip(a_rows, e_rows):
        #    if a_row != e_row:
        #        print("breakpoint")
        assert a_rows == e_rows
