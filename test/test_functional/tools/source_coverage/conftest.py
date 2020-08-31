from polytropos.actions.consume.sourcecoverage.crawl import Crawl
from polytropos.actions.consume.sourcecoverage.pair import SourceTargetPair
from polytropos.actions.consume.sourcecoverage.result import SourceCoverageResult

from typing import Callable, Dict, Iterable, cast, Tuple, List

import pytest

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track
from polytropos.ontology.variable import VariableId

@pytest.fixture()
def source_half_spec() -> Callable:
    def _half_spec(cardinal: int, ordinal: str, prefix: str, data_type: str) -> Dict:
        stage: str = "source"
        return {
            "%s_%s_folder_%i" % (stage, prefix, cardinal): {
                "name": "%s_%s_%s_folder" % (stage, ordinal, prefix),
                "data_type": "Folder",
                "sort_order": 0
            },
            "%s_%s_folder_%s_%i_1" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_1" % (stage, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_folder_%i" % (stage, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_folder_%s_%i_2" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_2" % (stage, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_folder_%i" % (stage, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_list_%i" % (stage, prefix, cardinal): {
                "name": "%s_list" % stage,
                "data_type": "List",
                "parent": "%s_%s_folder_%i" % (stage, prefix, cardinal),
                "sort_order": 1
            },
            "%s_%s_list_%s_%i_1" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_1" % (stage, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_list_%i" % (stage, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_list_%s_%i_2" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_2" % (stage, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_list_%i" % (stage, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_keyed_list_%i" % (stage, prefix, cardinal): {
                "name": "%s_keyed_list" % stage,
                "data_type": "KeyedList",
                "parent": "%s_%s_list_%i" % (stage, prefix, cardinal),
                "sort_order": 1
            },
            "%s_%s_keyed_list_%s_%i_1" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_1" % (stage, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_keyed_list_%i" % (stage, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_keyed_list_%s_%i_2" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_2" % (stage, data_type.lower()),
                "data_type": data_type,
                "parent": "%s_%s_keyed_list_%i" % (stage, prefix, cardinal),
                "sort_order": 0
            },
            "%s_%s_root_%s_%i_1" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_root_%s_%i_1" % (stage, prefix, data_type.lower(), cardinal),
                "data_type": data_type,
                "sort_order": 1
            },
            "%s_%s_root_%s_%i_2" % (stage, prefix, data_type.lower(), cardinal): {
                "name": "%s_%s_root_%s_%i_2" % (stage, prefix, data_type.lower(), cardinal),
                "data_type": data_type,
                "sort_order": 1
            }
        }
    return _half_spec

@pytest.fixture()
def source_track(source_half_spec) -> Callable:
    def _track(track_name: str, data_type: str) -> Track:
        first_half: Dict = source_half_spec(1, "first", track_name[0], data_type)
        second_half: Dict = source_half_spec(2, "second",  track_name[0], data_type)
        spec: Dict = {**first_half, **second_half}
        return Track.build(spec, None, track_name)
    return _track

@pytest.fixture()
def source_schema(source_track) -> Callable:
    def _source_schema(data_type: str = "Text") -> Schema:
        temporal: Track = source_track("temporal", data_type)
        immutable: Track = source_track("immutable", data_type)
        return Schema(temporal, immutable, name="source")
    return _source_schema

@pytest.fixture()
def target_spec() -> Callable:
    """
    +-- target_t_folder (target_t_folder)
    |   |
    |   +-- target_text_1 (target_t_folder_text_1)
    |   |
    |   +-- target_text_2 (target_t_folder_text_2)
    |   |
    |   +-- target_list (target_t_list)
    |       |
    |       +-- target_text_1 (target_t_list_text_1)
    |       |
    |       +-- target_text_2 (target_t_list_text_2)
    |       |
    |       +-- target_keyed_list (target_t_keyed_list)
    |           |
    |           +-- target_text_1 (target_t_keyed_list_text_1)
    |           |
    |           +-- target_text_2 (target_t_keyed_list_text_2)
    |
    +-- target_t_root_text_1 (target_t_root_text_1)
    |
    +-- target_t_root_text_2 (target_t_root_text_2)

    :return:
    """
    def _target_spec(prefix: str, data_type: str) -> Dict:
        return {
            "target_%s_folder" % prefix: {
                "name": "target_%s_folder" % prefix,
                "data_type": "Folder",
                "sort_order": 0
            },
            "target_%s_folder_%s_1" % (prefix, data_type.lower()): {
                "name": "target_%s_1" % data_type.lower(),
                "data_type": data_type,
                "parent": "target_%s_folder" % prefix,
                "sort_order": 0,
                "sources": ["source_%s_folder_%s_%i_1" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_folder_%s_2" % (prefix, data_type.lower()): {
                "name": "target_%s_2" % data_type.lower(),
                "data_type": data_type,
                "parent": "target_%s_folder" % prefix,
                "sort_order": 1,
                "sources": ["source_%s_folder_%s_%i_2" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_list" % prefix: {
                "name": "target_list",
                "data_type": "List",
                "parent": "target_%s_folder" % prefix,
                "sort_order": 2,
                "sources": ["source_%s_list_%i" % (prefix, index) for index in (1, 2)]
            },
            "target_%s_list_%s_1" % (prefix, data_type.lower()): {
                "name": "target_%s_1" % data_type.lower(),
                "data_type": data_type,
                "parent": "target_%s_list" % prefix,
                "sort_order": 0,
                "sources": ["source_%s_list_%s_%i_1" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_list_%s_2" % (prefix, data_type.lower()): {
                "name": "target_%s_2" % data_type.lower(),
                "data_type": data_type,
                "parent": "target_%s_list" % prefix,
                "sort_order": 1,
                "sources": ["source_%s_list_%s_%i_2" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_keyed_list" % prefix: {
                "name": "target_keyed_list",
                "data_type": "KeyedList",
                "parent": "target_%s_list" % prefix,
                "sort_order": 2,
                "sources": ["source_%s_keyed_list_%i" % (prefix, index) for index in (1, 2)]
            },
            "target_%s_keyed_list_%s_1" % (prefix, data_type.lower()): {
                "name": "target_%s_1" % data_type.lower(),
                "data_type": data_type,
                "parent": "target_%s_keyed_list" % prefix,
                "sort_order": 0,
                "sources": ["source_%s_keyed_list_%s_%i_1" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_keyed_list_%s_2" % (prefix, data_type.lower()): {
                "name": "target_%s_2" % data_type.lower(),
                "data_type": data_type,
                "parent": "target_%s_keyed_list" % prefix,
                "sort_order": 1,
                "sources": ["source_%s_keyed_list_%s_%i_2" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_root_%s_1" % (prefix, data_type.lower()): {
                "name": "target_%s_root_%s_1" % (prefix, data_type.lower()),
                "data_type": data_type,
                "sort_order": 1,
                "sources": ["source_%s_root_%s_%i_1" % (prefix, data_type.lower(), index) for index in (1, 2)]
            },
            "target_%s_root_%s_2" % (prefix, data_type.lower()): {
                "name": "target_%s_root_%s_2" % (prefix, data_type.lower()),
                "data_type": data_type,
                "sort_order": 2,
                "sources": ["source_%s_root_%s_%i_2" % (prefix, data_type.lower(), index) for index in (1, 2)]
            }
        }
    return _target_spec

@pytest.fixture()
def target_schema(target_spec: Callable) -> Callable:
    def _target_schema(source: Schema, data_type: str = "Text") -> Schema:
        temporal_spec: Dict = target_spec("t", data_type)
        temporal: Track = Track.build(temporal_spec, source.temporal, "temporal")
        immutable_spec: Dict = target_spec("i", data_type)
        immutable: Track = Track.build(immutable_spec, source.immutable, "immutable")
        return Schema(temporal, immutable, name="target", source=source)
    return _target_schema

@pytest.fixture()
def as_result() -> Callable:
    def _as_result(counts: Iterable[Tuple[str, str, int]]) -> SourceCoverageResult:
        ret: SourceCoverageResult = SourceCoverageResult()
        for source_var_str, target_var_str, n_obs in counts:
            source_var: VariableId = cast(VariableId, source_var_str)
            target_var: VariableId = cast(VariableId, target_var_str)
            pair: SourceTargetPair = SourceTargetPair(source_var, target_var)
            ret.pair_counts[pair] = n_obs
        return ret
    return _as_result

@pytest.fixture()
def do_crawl_test(source_schema: Callable, target_schema: Callable, as_result) -> Callable:
    def _do_unit_test(translation: Dict, trace: Dict, expected_pair_counts: List[Tuple[str, str, int]],
                      data_type: str = "Text") -> None:

        source: Schema = source_schema(data_type)
        target: Schema = target_schema(source, data_type)

        crawl: Crawl = Crawl("subject", target)
        actual: SourceCoverageResult = crawl(translation, trace)
        expected: SourceCoverageResult = as_result(expected_pair_counts)
        assert actual == expected
    return _do_unit_test

