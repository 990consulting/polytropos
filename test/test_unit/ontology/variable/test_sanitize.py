import pytest
from polytropos.ontology.variable import Text
from polytropos.ontology.variable.__primitive import EIN

@pytest.mark.parametrize("original, expected", [
    (None, None),
    ("", ""),
    ("/El Niño/", "el-ni%C3%B1o"),
    ("I'm a little \"teapot\", 'short' & stout.", "im-a-little-teapot-short-and-stout"),
    ("#yolo", "yolo"),
    ("Everyone was rude; Paris vacation", "everyone-was-rude-paris-vacation"),
    ("Mission: Impossible", "mission-impossible"),
    ("snake_case", "snake-case"),
    ("Either/or", "either-or"),
    ("(parenthesized)", "parenthesized"),
    (".net", "net")
])
def test_sanitize_text(original: str, expected: str) -> None:
    actual: str = Text.sanitize(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    ("012345678", "012345678"),
    ("01-2345678", "012345678"),
    ("  012345678 ", "012345678"),
    (" -0-1-2-3-4-5-6-7-8- ", "012345678"),
    ("abcdefghi", "abcdefghi"),
    ("abcdefghi", "abcdefghi"),
    ("12345678", "012345678"),
    ("bcdefghi", "bcdefghi"),
    ("00000008", "000000008"),
    ("8", "8"),
])
def test_sanitize_ein(original: str, expected: str) -> None:
    actual: str = EIN.sanitize(original)
    assert actual == expected

@pytest.mark.parametrize("original, expected", [
    ("012345678", "01-2345678"),
    ("01-2345678", "01-2345678"),
    ("  012345678 ", "01-2345678"),
    (" -0-1-2-3-4-5-6-7-8- ", "01-2345678"),
    ("abcdefghi", ""),
    ("abcdefghi", ""),
    ("12345678", "01-2345678"),
    ("bcdefghi", ""),
    ("00000008", "00-0000008"),
    ("8", ""),
])
def test_display_format_ein(original: str, expected: str) -> None:
    actual: str = EIN.display_format(original)
    assert actual == expected
