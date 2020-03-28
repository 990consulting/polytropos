import logging
import os
import shutil

import pytest

from polytropos.actions import register_all

WORKING_PATH: str = os.path.join("/tmp/polytropos_logical_operators_test")

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    shutil.rmtree(WORKING_PATH, ignore_errors=True)
    register_all()
    yield
    shutil.rmtree(WORKING_PATH, ignore_errors=True)

def test_simple(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    run_task('s_9_logical_operators', 'simple', 'generic/expected/simple', output_dir=WORKING_PATH)

def test_nested(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    run_task('s_9_logical_operators', 'nested', 'generic/expected/nested', output_dir=WORKING_PATH)

def test_nested_all(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    run_task('s_9_logical_operators', 'nested_all', 'generic/expected/nested_all', output_dir=WORKING_PATH)

def test_nested_without_narrow(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()
    run_task('s_9_logical_operators', 'nested_without_narrow', 'generic/expected/nested_without_narrow', output_dir=WORKING_PATH)

def test_illegal_usage(run_task):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    register_all()

    with pytest.raises(ValueError, match="LogicalOperator filter can be used in NestedFilter only"):
        run_task('s_9_logical_operators', 'illegal_usage', 'generic/expected/illegal_usage', output_dir=WORKING_PATH)
