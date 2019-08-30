import os
from unittest.mock import MagicMock

import pytest
from typing import Callable, List, Dict, Tuple

import yaml

from polytropos.actions.consume.tocsv.blocks import Block, ImmutableBlock, TemporalBlock
from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.descriptors.fromraw import GetAllBlocks

@pytest.fixture()
def abv() -> AsBlockValue:
    return MagicMock(spec=AsBlockValue)

@pytest.fixture()
def do_test(basepath, abv) -> Callable:
    task_dir: str = os.path.join(basepath, "..", "examples", "s_7_csv", "conf", "tasks")
    get_all_blocks: GetAllBlocks = GetAllBlocks(abv)

    def _do_test(filename: str, expected: List[Block]):
        task_path: str = os.path.join(task_dir, filename)
        with open(task_path) as fh:
            task_spec: Dict = yaml.full_load(fh)
        column_spec: List = task_spec["steps"][0]["Consume"]["columns"]
        actual: List[Block] = get_all_blocks(column_spec)
        assert actual == expected

    return _do_test

@pytest.fixture()
def i_block(abv) -> Callable:

    def _i_block(contents: Tuple) -> ImmutableBlock:
        return ImmutableBlock(contents, abv)

    return _i_block

@pytest.fixture()
def t_block() -> Callable:
    as_block_value: AsBlockValue = MagicMock(spec=AsBlockValue)

    def _t_block(contents: Tuple) -> TemporalBlock:
        return TemporalBlock(contents, as_block_value)

    return _t_block

def test_immutable_singleton(do_test, i_block):
    filename: str = "01_immutable_singleton.yaml"
    expected: List[Block] = [i_block(("i_text_in_folder",))]
    do_test(filename, expected)

def test_immutable_singleton_custom_name(do_test, i_block):
    filename: str = "03_immutable_singleton_custom_name.yaml"
    expected: List[Block] = [i_block(("i_text_in_folder",))]
    do_test(filename, expected)

def test_immutable_and_temporal_singletons(do_test, i_block, t_block):
    filename: str = "04_immutable_and_temporal_singletons.yaml"
    expected: List[Block] = [
        i_block(("i_text_in_folder",)),
        t_block(("t_text_in_folder",))
    ]
    do_test(filename, expected)

def test_temporal_list_and_immutable_named_list(do_test, i_block, t_block):
    filename: str = "05_temporal_list_and_immutable_named_list.yaml"
    expected: List[Block] = [
        t_block((("t_list_in_root", "t_text_in_list"),)),
        i_block((("i_named_list_in_root", "i_text_in_named_list"),))
    ]
    do_test(filename, expected)
