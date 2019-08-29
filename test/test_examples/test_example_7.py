import os

import polytropos.actions
import pytest
import shutil

BASEPATH = os.path.dirname(os.path.abspath(__file__))
WORKING_PATH: str = os.path.join("/tmp/polytropos_csv_test")

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    fixture_path: str = os.path.join(BASEPATH, "..", "..", "examples", "s_7_csv")
    shutil.rmtree(WORKING_PATH, ignore_errors=True)
    shutil.copytree(fixture_path, WORKING_PATH)
    polytropos.actions.register_all()

    yield
    shutil.rmtree(WORKING_PATH, ignore_errors=True)
