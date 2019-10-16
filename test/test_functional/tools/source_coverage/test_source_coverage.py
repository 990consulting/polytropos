import csv
import os
import random
import shutil
import string
from typing import Callable, Dict
import pytest

from polytropos.actions.consume.source_coverage import SourceCoverageFile
from polytropos.ontology.context import Context

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track


@pytest.fixture(scope="module")
def half_spec() -> Callable:
    def _half_spec(area: str, cardinal: int, ordinal: str, prefix: str, track_name: str, data_type: str = "Text") -> Dict:
        name_prefix = ""
        if area == "source":
            name_prefix = "source_"

        return {
            "%s_%s_folder_%i" % (area, prefix, cardinal): {
                "name": "%s%s_%s_folder" % (name_prefix, ordinal, track_name),
                "data_type": "Folder",
                "sort_order": 0
            },
            "%s_%s_folder_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_text_1" % name_prefix,
                "data_type": "Text",
                "parent": "%s_%s_folder_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_folder_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_text_2" % name_prefix,
                "data_type": "Text",
                "parent": "%s_%s_folder_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_list_%i" % (area, prefix, cardinal): {
                "name": "%sa_list" % name_prefix,
                "data_type": "List",
                "parent": "%s_%s_folder_%i" % (area, prefix, cardinal),
                "sort_order": 1
            },
            "%s_%s_list_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_1" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_list_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_2" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_keyed_list_%i" % (area, prefix, cardinal): {
                "name": "%sa_keyed_list" % name_prefix,
                "data_type": "KeyedList",
                "parent": "%s_%s_list_%i" % (area, prefix, cardinal),
                "sort_order": 1
            },
            "%s_%s_keyed_list_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_1" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_keyed_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_keyed_list_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%ssome_%s_2" % (name_prefix, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_keyed_list_%i" % (area, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_root_%s_%i_1" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%s%s_root_%s_%i_1" % (name_prefix, track_name, data_type.lower(), cardinal),
                "data_type": data_type,
                "sort_order": 1
            },
            "%s_%s_root_%s_%i_2" % (area, prefix, data_type.lower(), cardinal): {
                "name": "%s%s_root_%s_%i_2" % (name_prefix, track_name, data_type.lower(), cardinal),
                "data_type": data_type,
                "sort_order": 1
            }
        }
    return _half_spec


@pytest.fixture(scope="module")
def module_source_track(half_spec) -> Callable:
    def _track(prefix, track_name) -> Track:
        first_half: Dict = half_spec("source", 1, "first", prefix, track_name)
        second_half: Dict = half_spec("source", 2, "second", prefix, track_name)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track


@pytest.fixture(scope="module")
def module_source_schema(module_source_track) -> Schema:
    temporal: Track = module_source_track("t", "temporal")
    immutable: Track = module_source_track("i", "immutable")
    return Schema(temporal, immutable)


@pytest.fixture(scope="module")
def module_target_track(half_spec) -> Callable:
    def _track(prefix, track_name) -> Track:
        first_half: Dict = half_spec("target", 1, "first", prefix, track_name)
        second_half: Dict = half_spec("target", 2, "second", prefix, track_name)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track


@pytest.fixture(scope="module")
def module_target_schema(module_source_schema, module_target_track) -> Schema:
    temporal: Track = module_target_track("t", "temporal")
    immutable: Track = module_target_track("i", "immutable")
    target_schema = Schema(temporal, immutable)
    target_schema.source = module_source_schema
    return target_schema


@pytest.fixture(scope="module")
def module_basepath():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def output_basepath() -> str:
    dirname: str = ''.join([random.choice(string.ascii_letters) for n in range(10)])
    return "/tmp/%s" % dirname


@pytest.fixture(scope="module")
def do_run(module_basepath: str, module_target_schema: Schema, output_basepath) -> Callable:
    def _do_run():
        translate_dir: str = os.path.join(module_basepath, "translate")
        trace_dir: str = os.path.join(module_basepath, "trace")
        with Context.build(conf_dir="dummy", data_dir="dummy", output_dir=output_basepath) as context:
            coverage: SourceCoverageFile = SourceCoverageFile(context, module_target_schema, translate_dir, trace_dir)
            coverage("dummy", "dummy")
    return _do_run


@pytest.fixture(scope="module", autouse=True)
def setup(do_run, output_basepath) -> None:
    os.mkdir(output_basepath)
    do_run()

    yield

    shutil.rmtree(output_basepath)


def test_files_match(module_basepath, output_basepath):
    expected_path: str = os.path.join(module_basepath, "expected", "source_coverage.csv")
    actual_path: str = os.path.join(output_basepath, "source_coverage.csv")
    with open(expected_path) as expected_fh, open(actual_path) as actual_fh:
        expected: csv.DictReader = csv.DictReader(expected_fh)
        actual: csv.DictReader = csv.DictReader(actual_fh)
        e_rows = [row for row in expected]
        a_rows = [row for row in actual]
        #for a_row, e_row in zip(a_rows, e_rows):
        #    if a_row != e_row:
        #        print("breakpoint")
        assert a_rows == e_rows
