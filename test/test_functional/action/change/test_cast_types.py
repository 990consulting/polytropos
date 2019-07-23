import pytest

@pytest.mark.parametrize("raw, native", [
    ('foo bar', 'foo bar'),
    ('hello, friend', 'hello, friend'),
    ('"this" "is" "quoted"', '"this" "is" "quoted"')
])
def test_text(raw: str, native: str):
    pytest.fail()

@pytest.mark.parametrize("raw, native", [
    ("-10", -10),
    ("10", 10),
    (10, 10),
    (-10, -10)
])
def test_integer(raw: str, native: int):
    pytest.fail()

@pytest.mark.parametrize("raw", ["-10.0", "10.0", "spam"])
def test_integer_fails(raw: str):
    pytest.fail()

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
def test_decimal(raw: str, native: float):
    pytest.fail()

@pytest.mark.parametrize("raw", ["spam"])
def test_decimal_fails(raw: str):
    pytest.fail()

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
def test_currency(raw: str, native: float):
    pytest.fail()

@pytest.mark.parametrize("raw", ["spam"])
def test_currency_fails(raw: str):
    pytest.fail()

@pytest.mark.parametrize("raw", ["X", "x", True])
def test_unary_true(raw: str):
    pytest.fail()

@pytest.mark.parametrize("raw", ["True", "TRUE", "1", True])
def test_binary_true(raw: str):
    pytest.fail()

@pytest.mark.parametrize("raw", ["False", "FALSE", "0", False])
def test_binary_false(raw: str):
    pytest.fail()

@pytest.mark.parametrize("raw", ["10", "^10.0", "spam"])
def test_binary_fails(raw: str):
    pytest.fail()

@pytest.mark.parametrize("raw", ["TRUE", "true", "10", "^10.0", "spam", "false", "yes", "no", False])
def test_unary_fails(raw: str):
    pytest.fail()

@pytest.mark.parametrize("raw, expected", [
    ("2018-10-27", "2018-10-27"),
    ("201810", "2018-10-01"),
    ("000000", None)
])
def test_date(raw: str, expected: str):
    pytest.fail()

@pytest.mark.parametrize("raw", ["10/27/2018", "10/27/18", "spam"])
def test_date_fails(raw: str):
    pytest.fail()

@pytest.mark.parametrize("data_type", ["phone", "email", "url"])
def test_stringlike_unmodified(data_type: str):
    """Certain data types are essentially strings, but are distinguished for semantic purposes in downstream analyses.
     These should not be modified during the cast process."""
    pytest.fail()
