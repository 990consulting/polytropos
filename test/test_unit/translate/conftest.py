from unittest.mock import Mock

import pytest

@pytest.fixture()
def translator() -> Mock:
    class Source:
        def __getitem__(self, var_id: str) -> Mock():
            return Mock(var_id=var_id)

    return Mock(source=Source())


@pytest.fixture()
def document() -> Mock:
    return Mock()


@pytest.fixture()
def variable() -> Mock:
    return Mock()
