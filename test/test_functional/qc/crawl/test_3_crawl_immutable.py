"""Crawling immutable is nearly identical to crawling a period, so these tests are a subset of the simple case for
CrawlPeriod."""

import pytest

def test_empty_both():
    """Outcomes should remain empty."""
    pytest.fail()

def test_empty_fixture():
    """Outcomes should remain empty, even though actual has values."""
    pytest.fail()

def test_empty_actual():
    """Everything should be reported as missing."""
    pytest.fail()

def test_identical_simple():
    """Everything should be reported as matches."""
    pytest.fail()

def test_mismatch_simple():
    """All same except for one item."""
    pytest.fail()
