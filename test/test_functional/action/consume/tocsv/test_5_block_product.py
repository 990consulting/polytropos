from typing import Callable, List

import pytest
from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue

from polytropos.ontology.composite import Composite

from polytropos.actions.consume.tocsv.blocks import Block, BlockProduct, ImmutableBlock, TemporalBlock

@pytest.fixture()
def do_test(read_composite) -> Callable:
    composite: Composite = read_composite(4)

    def _do_test(blocks: List[Block], expected: List):
        product: BlockProduct = BlockProduct(composite, blocks)
        actual: List = list(product())
        assert actual == expected

    return _do_test

@pytest.fixture()
def abv(schema) -> AsBlockValue:
    return AsBlockValue(schema)

def test_immutable_singleton(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock(("i_text_in_folder",), abv)
    ]
    expected: List = [["composite_4", "I(folder)"]]
    do_test(blocks, expected)

def test_temporal_singleton(do_test, abv):
    blocks: List[Block] = [
        TemporalBlock(("t_text_in_folder",), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "P1(folder)"],
        ["composite_4", "period_2", "P2(folder)"]
    ]
    do_test(blocks, expected)

def test_two_temporal_singleton_blocks(do_test, abv):
    blocks: List[Block] = [
        TemporalBlock(("t_text_in_root",), abv),
        TemporalBlock(("t_text_in_folder",), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "P1(root)", "P1(folder)"],
        ["composite_4", "period_2", "P2(root)", "P2(folder)"]
    ]
    do_test(blocks, expected)

def test_temporal_and_immutable_singletons(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock(("i_text_in_folder",), abv),
        TemporalBlock(("t_text_in_folder",), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "I(folder)", "P1(folder)"],
        ["composite_4", "period_2", "I(folder)", "P2(folder)"]
    ]
    do_test(blocks, expected)

def test_temporal_list(do_test, abv):
    blocks: List[Block] = [TemporalBlock((("t_list_in_root", "t_text_in_list"),), abv)]
    expected: List = [
        ["composite_4", "period_1", None],
        ["composite_4", "period_2", "P2(list)(A)"],
        ["composite_4", "period_2", "P2(list)(B)"]
    ]
    do_test(blocks, expected)

def test_immutable_block_with_keyed_list(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock((("i_keyed_list_in_root", "i_text_in_keyed_list"), "i_text_in_folder"), abv)
    ]
    expected: List = [
        ["composite_4", "nl_1", "111", "I(folder)"],
        ["composite_4", "nl_2", "222", "I(folder)"]
    ]
    do_test(blocks, expected)

def test_two_immutable_blocks(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock((("i_keyed_list_in_root", "i_text_in_keyed_list"),), abv),
        ImmutableBlock(("i_text_in_folder",), abv)
    ]
    expected: List = [
        ["composite_4", "nl_1", "111", "I(folder)"],
        ["composite_4", "nl_2", "222", "I(folder)"]
    ]
    do_test(blocks, expected)

def test_immutable_singleton_and_temporal_list(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock(("i_text_in_folder",), abv),
        TemporalBlock((("t_list_in_root", "t_text_in_list"),), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "I(folder)", None],
        ["composite_4", "period_2", "I(folder)", "P2(list)(A)"],
        ["composite_4", "period_2", "I(folder)", "P2(list)(B)"]
    ]
    do_test(blocks, expected)

def test_immutable_keyed_list_and_temporal_singleton(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock((("i_keyed_list_in_root", "i_text_in_keyed_list"),), abv),
        TemporalBlock(("t_text_in_folder",), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "nl_1", "111", "P1(folder)"],
        ["composite_4", "period_1", "nl_2", "222", "P1(folder)"],
        ["composite_4", "period_2", "nl_1", "111", "P2(folder)"],
        ["composite_4", "period_2", "nl_2", "222", "P2(folder)"]
    ]
    do_test(blocks, expected)

def test_temporal_list_and_immutable_keyed_list(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock((("i_keyed_list_in_root", "i_text_in_keyed_list"),), abv),
        TemporalBlock((("t_list_in_root", "t_text_in_list"),), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "nl_1", "111", None],
        ["composite_4", "period_1", "nl_2", "222", None],
        ["composite_4", "period_2", "nl_1", "111", "P2(list)(A)"],
        ["composite_4", "period_2", "nl_1", "111", "P2(list)(B)"],
        ["composite_4", "period_2", "nl_2", "222", "P2(list)(A)"],
        ["composite_4", "period_2", "nl_2", "222", "P2(list)(B)"]
    ]
    do_test(blocks, expected)

def test_alternating(do_test, abv):
    blocks: List[Block] = [
        ImmutableBlock((("i_keyed_list_in_root", "i_text_in_keyed_list"),), abv),
        TemporalBlock(("t_text_in_folder",), abv),
        ImmutableBlock(("i_text_in_folder",), abv),
        TemporalBlock((("t_list_in_root", "t_text_in_list"),), abv)
    ]
    expected: List = [
        ["composite_4", "period_1", "nl_1", "111", "P1(folder)", "I(folder)", None],
        ["composite_4", "period_1", "nl_2", "222", "P1(folder)", "I(folder)", None],
        ["composite_4", "period_2", "nl_1", "111", "P2(folder)", "I(folder)", "P2(list)(A)"],
        ["composite_4", "period_2", "nl_1", "111", "P2(folder)", "I(folder)", "P2(list)(B)"],
        ["composite_4", "period_2", "nl_2", "222", "P2(folder)", "I(folder)", "P2(list)(A)"],
        ["composite_4", "period_2", "nl_2", "222", "P2(folder)", "I(folder)", "P2(list)(B)"]
    ]
    do_test(blocks, expected)
