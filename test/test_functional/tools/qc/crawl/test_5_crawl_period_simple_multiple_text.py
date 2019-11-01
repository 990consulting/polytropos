import copy
import json
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
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
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
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }
    observed: Dict = {}

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/some_multiple_text", "MultipleText", json.dumps(fixture["some_multiple_text"])))
    expected.missings.append(MissingValue(entity_id, period, "/outer/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["some_multiple_text"])))
    expected.missings.append(MissingValue(entity_id, period, "/outer/inner/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["inner"]["some_multiple_text"])))
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observed, actual, period)
    crawl()

    assert expected == actual

def test_null_actual(schema, period, entity_id):
    """Everything should be reported as missing."""
    fixture: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/some_multiple_text", "MultipleText", json.dumps(fixture["some_multiple_text"])))
    expected.missings.append(MissingValue(entity_id, period, "/outer/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["some_multiple_text"])))
    expected.missings.append(MissingValue(entity_id, period, "/outer/inner/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["inner"]["some_multiple_text"])))
    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, None, actual, period)
    crawl()

    assert expected == actual

def test_identical_simple(schema, period, entity_id):
    """Everything should be reported as matches."""
    fixture: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }
    observation: Dict = copy.deepcopy(fixture)

    # 3 Matches
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_multiple_text", "MultipleText", json.dumps(fixture["some_multiple_text"])))
    expected.matches.append(ValueMatch(entity_id, period, "/outer/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["some_multiple_text"])))
    expected.matches.append(ValueMatch(entity_id, period, "/outer/inner/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["inner"]["some_multiple_text"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_explicit_null_match(schema, period, entity_id):
    fixture: Dict = {"some_multiple_text": None}
    observation: Dict = {"some_multiple_text": None}

    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_multiple_text", "MultipleText", None))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

@pytest.mark.parametrize("f_val, o_val", [
    (["foo", "bar"], None),
    (None, ["foo", "bar"])
])
def test_explicit_null_mismatch(schema, period, entity_id, f_val, o_val):
    fixture: Dict = {"some_multiple_text": f_val}
    observation: Dict = {"some_multiple_text": o_val}

    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, period, "/some_multiple_text", "MultipleText",
                                             None if f_val is None else json.dumps(f_val),
                                             None if o_val is None else json.dumps(o_val)))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_explicit_null_missing(schema, period, entity_id):
    fixture: Dict = {"some_multiple_text": None}
    observation: Dict = {}

    expected: Outcome = Outcome()
    expected.missings.append(MissingValue(entity_id, period, "/some_multiple_text", "MultipleText", None))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_mismatch_simple(schema, period, entity_id):
    """All same except for one item."""
    fixture: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }
    observation: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["aa"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }

    # 2 matches, 1 mismatch
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_multiple_text", "MultipleText", json.dumps(fixture["some_multiple_text"])))
    expected.matches.append(ValueMatch(entity_id, period, "/outer/inner/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["inner"]["some_multiple_text"])))
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["some_multiple_text"]), json.dumps(["aa"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_missing_mismatch_simple(schema, period, entity_id):
    """One mismatch, one missing item."""
    fixture: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }
    observation: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "inner": {
                "some_multiple_text": ["aaa", "bbb", "ccc"],
            }
        }
    }

    # 1 match, 1 mismatch, 1 missing
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_multiple_text", "MultipleText", json.dumps(fixture["some_multiple_text"])))
    expected.missings.append(MissingValue(entity_id, period, "/outer/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["some_multiple_text"])))
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer/inner/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["inner"]["some_multiple_text"]), json.dumps(["aaa", "bbb", "ccc"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual

def test_not_tested_simple(schema, period, entity_id):
    """One mismatch, one field omitted from fixture."""
    fixture: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "inner": {
                "some_multiple_text": ["xxx", "yyy"],
            }
        }
    }
    observation: Dict = {
        "some_multiple_text": ["x", "y"],
        "outer": {
            "some_multiple_text": ["xx", "yy"],
            "inner": {
                "some_multiple_text": ["aaa"],
            }
        }
    }

    # 1 match, 1 mismatch
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, period, "/some_multiple_text", "MultipleText", json.dumps(fixture["some_multiple_text"])))
    expected.mismatches.append(ValueMismatch(entity_id, period, "/outer/inner/some_multiple_text", "MultipleText", json.dumps(fixture["outer"]["inner"]["some_multiple_text"]), json.dumps(["aaa"])))

    actual: Outcome = Outcome()

    crawl: CrawlPeriod = CrawlPeriod(entity_id, schema, fixture, observation, actual, period)
    crawl()

    assert expected == actual
