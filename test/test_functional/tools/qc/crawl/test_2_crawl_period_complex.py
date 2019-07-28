"""Cursory tests of Crawl's integration with complex data type comparisons. Detailed tests for List and NamedList
comparisons are found in test/test_functional/qc/values."""

import copy
from typing import Dict
import json
import pytest

from polytropos.ontology.schema import Schema
from polytropos.tools.qc.crawl import CrawlPeriod
from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch, MissingValue

@pytest.fixture
def schema(empty_track, complex_track) -> Schema:
    return Schema(complex_track, empty_track)

def test_identical_complex(schema, period, entity_id):
    """Everything should be reported as matches."""
    fixture: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"}
                    ]
                }
            },
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "bar"}
                    ]
                }
            },
        ]
    }
    observed: Dict = copy.deepcopy(fixture)

    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/outer", "List", json.dumps(fixture["outer"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_mismatch_complex(schema, entity_id, period):
    """All same except for one item."""
    fixture: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"}
                    ]
                }
            },
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "bar"}
                    ]
                }
            },
        ]
    }
    observed: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "123"}
                    ]
                }
            },
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "bar"}
                    ]
                }
            },
        ]
    }
    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer", "List", json.dumps(fixture["outer"]),
                                             json.dumps(observed["outer"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_missing_complex(schema, entity_id, period):
    """All same except for one missing item."""
    fixture: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"}
                    ]
                }
            },
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "bar"}
                    ]
                }
            },
        ]
    }
    observed: Dict = {}

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/outer", "List",
                                          json.dumps(fixture["outer"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_not_tested_complex(schema, entity_id, period):
    """All tested fields same, but one field is omitted from fixture."""
    fixture: Dict = {}
    observed: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"}
                    ]
                }
            },
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "bar"}
                    ]
                }
            },
        ]
    }

    expected: Outcome = Outcome()
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_fixture_undefined_complex_raises(schema, period, entity_id):
    """Fixture contains an undefined field, resulting in an error state."""
    """All same except for one missing item."""
    fixture: Dict = {
        "outer": [
            {
                "not_a_thing": {
                    "inner": [
                        {"some_text": "foo"}
                    ]
                }
            },
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "bar"}
                    ]
                }
            },
        ]
    }
    observed: Dict = copy.deepcopy(fixture)
    outcome: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, outcome, period)
    with pytest.raises(ValueError):
        crawl()
