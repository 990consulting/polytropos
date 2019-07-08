import os

import pytest

@pytest.fixture
def basepath() -> str:
    return os.path.dirname(os.path.abspath(__file__))
