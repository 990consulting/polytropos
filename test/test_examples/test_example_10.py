import logging
import os
import shutil

import pytest

from polytropos.actions import register_all

WORKING_PATH: str = os.path.join("/tmp/polytropos_merge_test")

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    shutil.rmtree(WORKING_PATH, ignore_errors=True)
    register_all()
    yield
    shutil.rmtree(WORKING_PATH, ignore_errors=True)

def test_merge(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    run_task('s_10_merge', 'merge', 'expected', output_dir=WORKING_PATH)