import os
from typing import Set, List

import pytest
from polytropos.ontology.schema import Schema

from polytropos.tools.qc.findall import FixtureOutcomes
from polytropos.tools.qc.outcome import ValueMatch, ValueMismatch, MissingValue

BASEPATH = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture(scope="session")
def example_path() -> str:
    return os.path.join(BASEPATH, "../../examples", "s_6_findall")

@pytest.fixture(scope="session")
def outcomes(example_path) -> FixtureOutcomes:
    schema: Schema = Schema.load("conf/schemas/simple", base_path=example_path)

    fixture_path: str = os.path.join(example_path, "data", "fixtures")
    obs_path: str = os.path.join(example_path, "data", "observations")

    return FixtureOutcomes(schema, fixture_path, obs_path)

def test_matches(outcomes):
    expected: List[ValueMatch] = [
        ValueMatch("entity_2", "period_1", "/temporal_folder/temporal_folder_text", "Text", "000"),
        ValueMatch("entity_4", "immutable", "/immutable_root_text", "Text", "PQR"),
        ValueMatch("entity_4", "immutable", "/immutable_folder/immutable_folder_text", "Text", "333"),
    ]
    actual: List[ValueMatch] = list(outcomes.matches)
    assert actual == expected

def test_match_ids(outcomes):
    expected: List[str] = [
        "/entity_2/period_1/temporal_folder/temporal_folder_text",
        "/entity_4/immutable/immutable_root_text",
        "/entity_4/immutable/immutable_folder/immutable_folder_text"
    ]
    actual: List[str] = list(outcomes.match_ids)
    assert actual == expected

def test_mismatches(outcomes):
    expected: List[ValueMismatch] = [
        ValueMismatch("entity_2", "period_1", "/temporal_root_text", "Text", "GHI", "GGG"),
        ValueMismatch("entity_2", "immutable", "/immutable_root_text", "Text", "MNO", "MMM"),
    ]
    actual: List[ValueMismatch] = list(outcomes.mismatches)
    assert actual == expected

def test_mismatch_ids(outcomes):
    expected: List[str] = [
        "/entity_2/period_1/temporal_root_text",
        "/entity_2/immutable/immutable_root_text"
    ]
    actual: List[str] = list(outcomes.mismatch_ids)
    assert actual == expected

def test_missing_values(outcomes):
    expected: List[MissingValue] = [
        MissingValue("entity_2", "period_2", "/temporal_root_text", "Text", "JKL"),
        MissingValue("entity_2", "period_2", "/temporal_folder/temporal_folder_text", "Text", "111"),
        MissingValue("entity_2", "immutable", "/immutable_folder/immutable_folder_text", "Text", "222")
    ]
    actual: List[MissingValue] = list(outcomes.missing_values)
    assert actual == expected

def test_missing_value_ids(outcomes):
    expected: List[str] = [
        "/entity_2/period_2/temporal_root_text",
        "/entity_2/period_2/temporal_folder/temporal_folder_text",
        "/entity_2/immutable/immutable_folder/immutable_folder_text"
    ]
    actual: List[str] = list(outcomes.missing_value_ids)
    assert actual == expected

def test_no_actual(outcomes):
    expected: Set[str] = {"entity_1"}
    actual: Set[str] = outcomes.no_actual
    assert actual == expected
