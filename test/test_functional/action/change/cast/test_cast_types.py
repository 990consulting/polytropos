from collections.abc import Callable
from typing import Optional, Any, Dict

import pytest

from polytropos.actions.changes.cast import Cast
from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema

from polytropos.ontology.track import Track

@pytest.fixture()
def do_simple_test() -> Callable:
    def _do_simple_test(data_type: str, raw: Optional[Any], native: Optional[Any]):
        spec: Dict = {
            "var": {
                "name": "the_var",
                "data_type": data_type,
                "sort_order": 0
            }
        }
        immutable: Track = Track.build(spec, None, "immutable")
        temporal: Track = Track.build({}, None, "temporal")
        schema: Schema = Schema(temporal, immutable)
        content: Dict = {
            "immutable": {
                "the_var": raw
            }
        }
        composite: Composite = Composite(schema, content)
        cast: Cast = Cast(schema, {})
        cast(composite)

        expected: Dict = {
            "immutable": {
                "the_var": native
            }
        }
        actual: Dict = composite.content
        assert actual == expected

    return _do_simple_test

@pytest.fixture()
def do_cast_error_test() -> Callable:
    def _do_cast_error_test(data_type: str, raw: Optional[Any]):
        spec: Dict = {
            "var": {
                "name": "the_var",
                "data_type": data_type,
                "sort_order": 0
            }
        }
        immutable: Track = Track.build(spec, None, "immutable")
        temporal: Track = Track.build({}, None, "temporal")
        schema: Schema = Schema(temporal, immutable)
        content: Dict = {
            "immutable": {
                "the_var": raw
            }
        }
        composite: Composite = Composite(schema, content)
        cast: Cast = Cast(schema, {})
        cast(composite)

        expected: Dict = {
            "immutable": {
                "qc": {
                    "_exceptions": {
                        "cast_errors": {
                            "the_var": raw
                        }
                    }
                }
            }
        }
        actual: Dict = composite.content
        assert actual == expected

    return _do_cast_error_test

@pytest.mark.parametrize("raw, native", [
    ('foo bar', 'foo bar'),
    ('hello, friend', 'hello, friend'),
    ('"this" "is" "quoted"', '"this" "is" "quoted"')
])
def test_text(do_simple_test: Callable, raw: Any, native: str):
    do_simple_test("Text", raw, native)

@pytest.mark.parametrize("raw, native", [
    ("-10", -10),
    ("10", 10),
    (10, 10),
    (-10, -10)
])
def test_integer(do_simple_test: Callable, raw: Any, native: int):
    do_simple_test("Integer", raw, native)

@pytest.mark.parametrize("raw", ["-10.0", "10.0", "spam"])
def test_integer_fails(do_cast_error_test: Callable, raw: Any):
    do_cast_error_test("Integer", raw)

@pytest.mark.parametrize("raw,native", [
    ("-10.0", -10.0),
    ("10.0", 10.0),
    ("10", 10.0),
    ("-10", -10.0),
    (-10.0, -10.0),
    (10.0, 10.0),
    (10, 10.0),
    (-10, -10.0)
])
def test_decimal(do_simple_test: Callable, raw: Any, native: float):
    do_simple_test("Decimal", raw, native)

@pytest.mark.parametrize("raw", ["spam"])
def test_decimal_fails(do_cast_error_test: Callable, raw: Any):
    do_cast_error_test("Decimal", raw)

@pytest.mark.parametrize("raw,native", [
    ("-10.32", -10),
    ("10.70", 10),
    ("10", 10),
    ("-10", -10),
    (-10.0, -10),
    (10.0, 10),
    (10, 10),
    (-10, -10)
])
def test_currency(do_simple_test: Callable, raw: Any, native: float):
    do_simple_test("Currency", raw, native)

@pytest.mark.parametrize("raw", ["spam"])
def test_currency_fails(do_cast_error_test: Callable, raw: Any):
    do_cast_error_test("Decimal", raw)

@pytest.mark.parametrize("raw", ["X", "x", True])
def test_unary_true(do_simple_test: Callable, raw: Any):
    do_simple_test("Unary", raw, True)

@pytest.mark.parametrize("raw", ["TRUE", "true", "10", "^10.0", "spam", "false", "yes", "no", False])
def test_unary_fails(do_cast_error_test: Callable, raw: Any):
    do_cast_error_test("Unary", raw)

@pytest.mark.parametrize("raw", ["True", "TRUE", "1", True])
def test_binary_true(do_simple_test: Callable, raw: Any):
    do_simple_test("Binary", raw, True)

@pytest.mark.parametrize("raw", ["False", "FALSE", "0", False])
def test_binary_false(do_simple_test, raw: Any):
    do_simple_test("Binary", raw, False)

@pytest.mark.parametrize("raw", ["10", "^10.0", "spam"])
def test_binary_fails(do_cast_error_test: Callable, raw: Any):
    do_cast_error_test("Binary", raw)

@pytest.mark.parametrize("raw, native", [
    ("2018-10-27", "2018-10-27"),
    ("201810", "2018-10-01"),
    ("000000", None)
])
def test_date(do_simple_test: Callable, raw: Any, native: str):
    do_simple_test("Date", raw, native)

@pytest.mark.parametrize("raw", ["10/27/2018", "10/27/18", "spam"])
def test_date_fails(do_cast_error_test, raw: Any):
    do_cast_error_test("Date", raw)

@pytest.mark.parametrize("data_type", ["Phone", "Email", "URL"])
def test_stringlike_unmodified(do_simple_test: Callable, data_type: str):
    """Certain data types are essentially strings, but are distinguished for semantic purposes in downstream analyses.
     These should not be modified during the cast process."""
    do_simple_test(data_type, "foo", "foo")
