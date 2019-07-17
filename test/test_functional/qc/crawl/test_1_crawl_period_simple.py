import copy
from typing import Dict

import pytest
from polytropos.ontology.schema import Schema
from polytropos.tools.qc.crawl import CrawlPeriod
from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch, MissingValue

@pytest.fixture
def schema(empty_track, simple_track) -> Schema:
    return Schema(simple_track, empty_track)

def test_empty_both(schema, period, entity_id):
    """Outcomes should remain empty."""
    fixture: Dict = {}
    observed: Dict = {}

    expected: Outcome = Outcome()
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_empty_fixture(schema, period, entity_id):
    """Outcomes should remain empty, even though actual has values."""
    fixture: Dict = {}
    observed: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }

    expected: Outcome = Outcome()
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_empty_actual(schema, period, entity_id):
    """Everything should be reported as missing."""
    fixture: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }
    observed: Dict = {}

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/some_text", "Text", "foo"))
    expected.missings.append(MissingValue(entity_id, period, "/outer/some_text", "Text", "bar"))
    expected.missings.append(MissingValue(entity_id, period, "/outer/inner/some_text", "Text", "baz"))
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_null_actual(schema, period, entity_id):
    """Everything should be reported as missing."""
    fixture: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/some_text", "Text", "foo"))
    expected.missings.append(MissingValue(entity_id, period, "/outer/some_text", "Text", "bar"))
    expected.missings.append(MissingValue(entity_id, period, "/outer/inner/some_text", "Text", "baz"))
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, None, actual, period)
    crawl()

    assert expected == actual

def test_identical_simple(schema, period, entity_id):
    """Everything should be reported as matches."""
    fixture: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }
    observation: Dict = copy.deepcopy(fixture)

    # 3 Matches
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_text", "Text", "foo"))
    expected.matches.append(ValueMatch(entity_id, period, "/outer/some_text", "Text", "bar"))
    expected.matches.append(ValueMatch(entity_id, period, "/outer/inner/some_text", "Text", "baz"))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_explicit_null_match(schema, period, entity_id):
    fixture: Dict = {"some_text": None}
    observation: Dict = {"some_text": None}

    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_text", "Text", None))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

@pytest.mark.parametrize("f_val, o_val", [
    ("foo", None),
    (None, "foo")
])
def test_explicit_null_mismatch(schema, period, entity_id, f_val, o_val):
    fixture: Dict = {"some_text": f_val}
    observation: Dict = {"some_text": o_val}

    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, period, "/some_text", "Text", f_val, o_val))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_explicit_null_missing(schema, period, entity_id):
    fixture: Dict = {"some_text": None}
    observation: Dict = {}

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/some_text", "Text", None))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_mismatch_simple(schema, period, entity_id):
    """All same except for one item."""
    fixture: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }
    observation: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "123",
            "inner": {
                "some_text": "baz"
            }
        }
    }

    # 2 matches, 1 mismatch
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_text", "Text", "foo"))
    expected.matches.append(ValueMatch(entity_id, period, "/outer/inner/some_text", "Text", "baz"))
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer/some_text", "Text", "bar", "123"))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_missing_mismatch_simple(schema, period, entity_id):
    """One mismatch, one missing item."""
    fixture: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }
    observation: Dict = {
        "some_text": "foo",
        "outer": {
            "inner": {
                "some_text": "123"
            }
        }
    }

    # 1 match, 1 mismatch, 1 missing
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_text", "Text", "foo"))
    expected.missings.append(MissingValue(entity_id, period, "/outer/some_text", "Text", "bar"))
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer/inner/some_text", "Text", "baz", "123"))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_not_tested_simple(schema, period, entity_id):
    """One mismatch, one field omitted from fixture."""
    fixture: Dict = {
        "some_text": "foo",
        "outer": {
            "inner": {
                "some_text": "123"
            }
        }
    }
    observation: Dict = {
        "some_text": "foo",
        "outer": {
            "some_text": "bar",
            "inner": {
                "some_text": "baz"
            }
        }
    }

    # 1 match, 1 mismatch
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_text", "Text", "foo"))
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer/inner/some_text", "Text", "123", "baz"))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

@pytest.mark.parametrize("observation", [
    {},
    {"not a thing": "blah blah"}
])
def test_fixture_undefined_raises(schema, period, entity_id, observation):
    """Fixture contains an undefined field, resulting in an error state."""
    fixture: Dict = {
        "not a thing": "blah blah"
    }
    outcome: Outcome = Outcome()
    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, outcome, period)
    with pytest.raises(ValueError):
        crawl()
