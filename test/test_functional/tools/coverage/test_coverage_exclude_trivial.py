import csv
import os
import random
import shutil
import string
from typing import Callable, Optional, Dict, List
import pytest

from polytropos.actions.consume.coverage import CoverageFile
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track


@pytest.fixture(scope="module")
def source_track(half_source_spec) -> Callable:
    def _track(prefix, track_name, data_type) -> Track:
        if data_type in ["List", "KeyedList", "Boolean"]:
            data_type = "Text"
        first_half: Dict = half_source_spec(1, "first", prefix, track_name, data_type)
        second_half: Dict = half_source_spec(2, "second", prefix, track_name, data_type)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track


@pytest.fixture(scope="module")
def source_schema(source_track) -> Callable:
    def _schema(data_type):
        temporal: Track = source_track("t", "temporal", data_type)
        immutable: Track = source_track("i", "immutable", data_type)
        return Schema(temporal, immutable)
    return _schema


@pytest.fixture(scope="module")
def data_types() -> List[str]:
    return ["Text", "Integer", "List", "KeyedList", "Boolean"]


@pytest.fixture(scope="module")
def module_basepath() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "exclude_trivial")


@pytest.fixture(scope="module")
def context() -> Context:
    ret: Context = Context.build(conf_dir="dummy", data_dir="dummy")
    return ret


@pytest.fixture(scope="module")
def output_basepath() -> str:
    dirname: str = ''.join([random.choice(string.ascii_letters) for n in range(10)])
    return "/tmp/%s" % dirname


@pytest.fixture(scope="module")
def do_run(module_basepath, source_schema: Callable, context, output_basepath) -> Callable:
    def _do_run(data_type: str, test_name: str, t_group_var: Optional[str], i_group_var: Optional[str]):
        composite_path: str = os.path.join(module_basepath, data_type.lower(), "composites")
        output_path: str = os.path.join(output_basepath, data_type.lower() + "/" + test_name + "/" + test_name)
        coverage: CoverageFile = CoverageFile(context, source_schema(data_type), output_path, t_group_var, i_group_var, exclude_trivial=True)
        coverage(composite_path, "dummy")
    return _do_run


@pytest.fixture(scope="module", autouse=True)
def setup(do_run, output_basepath, data_types) -> None:
    os.mkdir(output_basepath)
    for data_type in data_types:
        os.makedirs(os.path.join(output_basepath, data_type.lower(), "grouped"))
        os.makedirs(os.path.join(output_basepath, data_type.lower(), "ungrouped"))

        do_run(data_type, "ungrouped", None, None)
        do_run(data_type, "grouped", "source_t_folder_text_1", "source_i_folder_text_2")

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
def test_files_match(data_types, module_basepath, output_basepath, filename):
    for data_type in data_types:
        expected_path: str = os.path.join(module_basepath, data_type.lower(), filename)
        actual_path: str = os.path.join(output_basepath, data_type.lower(), filename)
        with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
            expected: csv.DictReader = csv.DictReader(expected_fh)
            actual: csv.DictReader = csv.DictReader(actual_fh)
            e_rows = [row for row in expected]
            a_rows = [row for row in actual]
            # for a_row, e_row in zip(a_rows, e_rows):
            #    if a_row != e_row:
            #        print("breakpoint")
            assert a_rows == e_rows



