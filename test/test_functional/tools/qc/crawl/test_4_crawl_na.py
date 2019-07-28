"""The special string value |--|NA|--| in a fixture indicates that the actual to which it corresponds should not have that
node at all. If the node is actually absent, the absence is recorded as a match. If the node is present, even as None,
it is recorded as a mismatch."""
from typing import Dict

import pytest

from polytropos.ontology.schema import Schema
from polytropos.tools.qc.crawl import CrawlImmutable
from polytropos.tools.qc.outcome import Outcome, ValueMatch, ValueMismatch

def test_simple_na_absent_match(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is missing in the actual, count it as a match."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "|--|NA|--|",
        "outer": {
            "some_text": "foo"
        }
    }
    observation: Dict = {
        "outer": {
            "some_text": "foo"
        }
    }
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, "immutable", "/some_text", "Text", "|--|NA|--|"))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/some_text", "Text", "foo"))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

def test_simple_na_present_as_none_mismatch(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is present in the actual with the value None, count it
    as a mismatch."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "|--|NA|--|",
        "outer": {
            "some_text": "foo"
        }
    }
    observation: Dict = {
        "some_text": None,
        "outer": {
            "some_text": "foo"
        }
    }
    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, "immutable", "/some_text", "Text", "|--|NA|--|", None))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/some_text", "Text", "foo"))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

def test_simple_na_present_with_value_mismatch(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is present in the actual with a non-null value, count it
    as a mismatch."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "|--|NA|--|",
        "outer": {
            "some_text": "foo"
        }
    }
    observation: Dict = {
        "some_text": "bar",
        "outer": {
            "some_text": "foo"
        }
    }
    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, "immutable", "/some_text", "Text", "|--|NA|--|", "bar"))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/some_text", "Text", "foo"))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

def test_simple_na_literal_raises(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--|, and the observation has that actual string literal, it raises an error
    so that we can change the sentinel value."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "|--|NA|--|",
        "outer": {
            "some_text": "foo"
        }
    }
    observation: Dict = {
        "some_text": "|--|NA|--|",
        "outer": {
            "some_text": "foo"
        }
    }
    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    with pytest.raises(ValueError):
        crawl()

def test_folder_na_absent_match(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is missing in the actual, count it as a match."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "bar",
        "outer": {
            "some_text": "|--|NA|--|"
        }
    }
    observation: Dict = {
        "some_text": "bar",
        "outer": {}
    }
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/some_text", "Text", "|--|NA|--|"))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/some_text", "Text", "bar"))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

def test_whole_folder_absent_match(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| nested inside a folder, and the whole folder is absent, that is a match
    (at least for that variable)."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "bar",
        "outer": {
            "some_text": "|--|NA|--|"
        }
    }
    observation: Dict = {
        "some_text": "bar"
    }
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer/some_text", "Text", "|--|NA|--|"))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/some_text", "Text", "bar"))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

def test_folder_na_present_as_none_mismatch(simple_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is present in the actual with the value None, count it
    as a mismatch."""
    schema: Schema = Schema(empty_track, simple_track)
    fixture: Dict = {
        "some_text": "bar",
        "outer": {
            "some_text": "|--|NA|--|",
        }
    }
    observation: Dict = {
        "some_text": "bar",
        "outer": {
            "some_text": None,
        }
    }
    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, "immutable", "/outer/some_text", "Text", "|--|NA|--|", None))
    expected.matches.append(ValueMatch(entity_id, "immutable", "/some_text", "Text", "bar"))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observation, actual)
    crawl()

    assert expected == actual

def test_list_na_absent_match(complex_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is missing in the actual, count it as a match."""
    schema: Schema = Schema(empty_track, complex_track)
    fixture: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"},
                        {"some_text": "|--|NA|--|"}
                    ],

                }
            }
        ]
    }
    observed: Dict = {
            "outer": [
                {
                    "the_folder": {
                        "inner": [
                            {"some_text": "foo"},
                            {}
                        ],

                    }
                }
            ]
    }
    expected: Outcome = Outcome()
    expected.matches.append(ValueMatch(entity_id, "immutable", "/outer", "List", fixture["outer"]))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observed, actual)
    crawl()

    assert expected == actual

def test_list_na_present_as_none_mismatch(complex_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item is present in the actual with the value None, count it
    as a mismatch."""
    schema: Schema = Schema(empty_track, complex_track)
    fixture: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"},
                        {"some_text": "|--|NA|--|"}
                    ],

                }
            }
        ]
    }
    observed: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"},
                        {"some_text": None}
                    ],

                }
            }
        ]
    }
    expected: Outcome = Outcome()
    expected.mismatches.append(ValueMismatch(entity_id, "immutable", "/outer", "List", fixture["outer"], observed["outer"]))

    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observed, actual)
    crawl()

    assert expected == actual

def test_list_na_literal_raises(complex_track, empty_track, entity_id):
    """If the fixture has an explicit |--|NA|--| and the item has the same string, an error is raised because we need
    to choose a new, truly unique sentinel value for missing data."""
    schema: Schema = Schema(empty_track, complex_track)
    fixture: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"},
                        {"some_text": "|--|NA|--|"}
                    ],

                }
            }
        ]
    }
    observed: Dict = {
        "outer": [
            {
                "the_folder": {
                    "inner": [
                        {"some_text": "foo"},
                        {"some_text": "|--|NA|--|"}
                    ],

                }
            }
        ]
    }
    actual: Outcome = Outcome()

    crawl: CrawlImmutable = CrawlImmutable(entity_id, schema, fixture, observed, actual)
    with pytest.raises(ValueError):
        crawl()
