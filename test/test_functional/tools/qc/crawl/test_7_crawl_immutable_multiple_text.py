"""Crawling immutable is nearly identical to crawling a period, so these tests are a subset of the simple case for
CrawlPeriod."""
import copy
import json
from typing import Dict

import pytest
from polytropos.ontology.schema import Schema
from polytropos.tools.qc.crawl import CrawlPeriod, CrawlImmutable
from polytropos.tools.qc.outcome import Outcome, MissingValue, ValueMatch

@pytest.fixture
def schema(empty_track, simple_track) -> Schema:
    return Schema(empty_track, simple_track)

def test_empty_both(schema, entity_id):
    """Outcomes should remain empty."""
    fixture: Dict = {}
    observed: Dict = {}

    expected: Outcome = Outcome()
    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observed, actual)
    crawl()

    assert expected == actual

def test_empty_fixture(schema, entity_id):
    """Outcomes should remain empty, even though actual has values."""
    fixture: Dict = {}
    observed: Dict = {
        "some_multiple_text": ["foo"],
        "outer": {
            "some_multiple_text": ["bar", "baq"],
            "inner": {
                "some_multiple_text": ["baz"]
            }
        }
    }

    expected: Outcome = Outcome()
    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observed, actual)
    crawl()

    assert expected == actual

def test_empty_actual(schema, entity_id):
    """Everything should be reported as missing."""
    fixture: Dict = {
        "some_multiple_text": ["foo"],
        "outer": {
            "some_multiple_text": ["bar", "baq"],
            "inner": {
                "some_multiple_text": ["baz"]
            }
        }
    }
    observed: Dict = {}

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, "immutable", "/some_multiple_text", "MultipleText", json.dumps(["foo"])))
    expected.missings.append(MissingValue(entity_id, "immutable", "/outer/some_multiple_text", "MultipleText", json.dumps(["bar", "baq"])))
    expected.missings.append(MissingValue(entity_id, "immutable", "/outer/inner/some_multiple_text", "MultipleText", json.dumps(["baz"])))
    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observed, actual)
    crawl()

    assert expected == actual

def test_identical_simple(schema, entity_id):
    """Everything should be reported as matches."""
    fixture: Dict = {
        "some_multiple_text": ["foo"],
        "outer": {
            "some_multiple_text": ["bar", "baq"],
            "inner": {
                "some_multiple_text": ["baz"]
            }
        }
    }
    observation: Dict = copy.deepcopy(fixture)

    # 3 Matches
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, "immutable", "/some_multiple_text", "MultipleText", json.dumps(["foo"])))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/some_multiple_text", "MultipleText", json.dumps(["bar", "baq"])))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/inner/some_multiple_text", "MultipleText", json.dumps(["baz"])))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

