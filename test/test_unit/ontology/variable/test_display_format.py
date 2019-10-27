from typing import Optional

import pytest
from polytropos.ontology.variable import URL, Phone, Decimal, Currency, Integer, Ratio, Unary, Binary

def _as_link(url: str) -> str:
    return URL.link_template.format(url, url)

@pytest.mark.parametrize("original, expected", [
    ("http//www.mylazyaccountant.com", _as_link("http://www.mylazyaccountant.com")),
    ("www.presumptuouspreparer.org", _as_link("http://www.presumptuouspreparer.org")),
    ("presumptuouspreparer.us", _as_link("http://presumptuouspreparer.us")),
    ("http://www.anachronisticurl.edu/~steve", _as_link("http://www.anachronisticurl.edu/~steve")),
    ("https://www.open990.org/org/012345678#steve", _as_link("https://www.open990.org/org/012345678#steve")),
    ("https://www.MyImplausibleUrl.com/ButCouldBeRight", _as_link("https://www.myimplausibleurl.com/butcouldberight"))
])
def test_url_valid_single(original: str, expected: str):
    actual: str = URL.display_format(original)
    assert actual == expected

def test_url_multiple_valid():
    original: str = "abc.com, xyz.org; mmm.gov"
    expected: str = ", ".join([_as_link(x) for x in ["http://abc.com", "http://xyz.org", "http://mmm.gov"]])
    actual: str = URL.display_format(original)
    assert actual == expected

def test_url_mixed_valid_invalid():
    original: str = "we like to put text in our url fields; but here's a real one, mysite.com"
    expected: str = "we like to put text in our url fields, but here's a real one, {:}".format(
        _as_link("http://mysite.com"))
    actual: str = URL.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original", [
    "https://username@password:mysketchywebsite.com",
    "http://localhost",
    "https://www.opendata.love/"
])
def test_url_website_reject(original: str):
    actual: str = URL.display_format(original)
    assert actual == original

def test_url_xkcd_sql_injection():
    original: str = "Robert'); DROP TABLE Students;--"
    expected: str = "Robert'), DROP TABLE Students, --"
    actual: str = URL.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original", ["N/A", "NA", "NONE", "None", None, ""])
def test_url_empty_cases(original: str):
    actual: str = URL.display_format(original)
    assert actual == ""

@pytest.mark.parametrize("original, expected", [
    ("", ""),
    (None, ""),
    ("(508) 867-5309", "(508) 867-5309"),
    ("N/A", "N/A"),
    ("867-5309 Jenny", "867-5309 Jenny"),
    ("5088675309", "+1 (508) 867-5309")
])
def test_phone(original: Optional[str], expected: str):
    actual: str = Phone.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    (None, ""),
    (1.0, "1.00"),
    (-27.6582, "-27.66"),
    (987654.321, "987,654.32")
])
def test_decimal(original: Optional[float], expected: str):
    actual: str = Decimal.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    (None, ""),
    (1, "$1"),
    (-27, "-$27"),
    (987654, "$987,654")
])
def test_currency(original: Optional[int], expected: str):
    actual: str = Currency.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    (None, ""),
    (1, "1"),
    (-27, "-27"),
    (9876543, "9,876,543")
])
def test_integer(original: Optional[int], expected: str):
    actual: str = Integer.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    (None, ""),
    (0.0, "0%"),
    (0.1, "10%"),
    (0.458, "46%"),
    (-0.458, "-46%"),
    (4000.0, "400,000%")
])
def test_ratio(original: Optional[float], expected: str):
    actual: str = Ratio.display_format(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    (None, ""),
    (True, "True")
])
def test_unary(original: Optional[bool], expected: str):
    actual: str = Unary.display_format(original)
    assert actual == expected

def test_unary_false_raises():
    with pytest.raises(AssertionError):
        Unary.display_format(False)

@pytest.mark.parametrize("original, expected", [
    (None, ""),
    (True, "Yes"),
    (False, "No")
])
def test_binary(original: Optional[bool], expected: str):
    actual: str = Binary.display_format(original)
    assert actual == expected