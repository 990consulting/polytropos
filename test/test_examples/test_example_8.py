import logging
import os
import shutil

import pytest

from polytropos.actions import register_all

WORKING_PATH: str = os.path.join("/tmp/polytropos_filter_narrow_test")

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    shutil.rmtree(WORKING_PATH, ignore_errors=True)
    register_all()
    yield
    shutil.rmtree(WORKING_PATH, ignore_errors=True)

# noinspection PyUnresolvedReferences
def test_sequential(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    import examples.s_8_filter_narrow.conf.filters.threshold
    run_task('s_8_filter_narrow', 'sequential', 'generic/expected', output_dir=WORKING_PATH)

def test_compound(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    import examples.s_8_filter_narrow.conf.filters.threshold
    run_task('s_8_filter_narrow', 'compound', 'generic/expected', output_dir=WORKING_PATH)
