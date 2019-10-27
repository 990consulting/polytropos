import pytest
from polytropos.ontology.variable import Text

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