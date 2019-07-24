import pytest

from polytropos.ontology.track import Track

@pytest.fixture
def empty_track() -> Track:
    return Track.build({}, None, "")
