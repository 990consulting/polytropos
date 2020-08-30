import csv
import os
import random
import shutil
import string
from typing import Callable, Dict, List
import pytest

from polytropos.actions.consume.source_coverage import SourceCoverage
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track


@pytest.fixture(scope="module")
def source_track(half_spec) -> Callable:
    def _track(prefix, track_name, data_type) -> Track:
        if data_type in ["List", "KeyedList"]:
            data_type = "Text"
        first_half: Dict = half_spec("source", 1, "first", prefix, track_name, data_type)
        second_half: Dict = half_spec("source", 2, "second", prefix, track_name, data_type)
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
def target_track(half_spec) -> Callable:
    def _track(prefix, track_name, data_type) -> Track:
        if data_type in ["List", "KeyedList"]:
            data_type = "Text"
        first_half: Dict = half_spec("target", 1, "first", prefix, track_name, data_type)
        second_half: Dict = half_spec("target", 2, "second", prefix, track_name, data_type)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track


@pytest.fixture(scope="module")
def target_schema(target_track, source_schema) -> Callable:
    def _schema(data_type):
        temporal: Track = target_track("t", "temporal", data_type)
        immutable: Track = target_track("i", "immutable", data_type)
        return Schema(temporal, immutable, source=source_schema(data_type))
    return _schema


data_types: List[str] = ["Text", "Integer", "List", "KeyedList"]


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
    return "/tmp/source_cvg_exclude_trivial_%s" % dirname


@pytest.fixture(scope="module")
def do_run(module_basepath: str, target_schema: Callable, output_basepath) -> Callable:
    def _do_run(data_type: str):
        translate_dir: str = os.path.join(module_basepath, data_type.lower(), "translate")
        trace_dir: str = os.path.join(module_basepath, data_type.lower(), "trace")
        output_dir: str = os.path.join(output_basepath, data_type.lower())
        with Context.build(conf_dir="dummy", data_dir="dummy", output_dir=output_dir) as context:
            coverage: SourceCoverage = SourceCoverage(context, target_schema(data_type), translate_dir, trace_dir)
            coverage("dummy", "dummy")
    return _do_run

@pytest.fixture(scope="module", autouse=True)
def setup(do_run, output_basepath) -> None:
    os.mkdir(output_basepath)
    for data_type in data_types:
        os.makedirs(os.path.join(output_basepath, data_type.lower()))
        do_run(data_type)

    #yield

    #shutil.rmtree(output_basepath)


@pytest.mark.parametrize("data_type", data_types)
def test_files_match(data_type, module_basepath, output_basepath):
    expected_path: str = os.path.join(module_basepath, data_type.lower(), "source_coverage.csv")
    actual_path: str = os.path.join(output_basepath, data_type.lower(), "source_coverage.csv")
    with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
        expected: csv.DictReader = csv.DictReader(expected_fh)
        actual: csv.DictReader = csv.DictReader(actual_fh)
        e_rows = [row for row in expected]
        a_rows = [row for row in actual]
        # for a_row, e_row in zip(a_rows, e_rows):
        #    if a_row != e_row:
        #        print("breakpoint")
        assert a_rows == e_rows



