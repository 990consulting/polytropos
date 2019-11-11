import itertools
from collections import deque
from typing import Dict, Tuple, List, Deque, Type

from dataclasses import dataclass, field

from polytropos.actions.consume.tocsv.blocks import Block, ImmutableBlock, TemporalBlock
from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.descriptors.colblocks import DescriptorBlockToColumnBlocks
from polytropos.actions.consume.tocsv.descriptors.colnames import DescriptorBlockToColumnNames

constructors: Dict[str, Type] = {
    "temporal_block": TemporalBlock,
    "immutable_block": ImmutableBlock
}

@dataclass
class GetAllColumnNames:
    spec_to_names: DescriptorBlockToColumnNames
    id_col_name: str

    def __call__(self, full_spec: List[Dict]) -> List[str]:
        has_temporal: bool = False
        block_columns: Deque[str] = deque()
        for block_spec in full_spec:  # type: Dict
            assert len(block_spec) == 1
            block_type: str = list(block_spec.keys())[0]
            assert block_type in {"temporal_block", "immutable_block"}
            if block_type == "temporal_block":
                has_temporal = True
            names_for_block = self.spec_to_names(block_spec[block_type])
            block_columns.extend(names_for_block)
        if has_temporal:
            return list(itertools.chain([self.id_col_name, "period"], block_columns))
        else:
            return list(itertools.chain([self.id_col_name], block_columns))

class GetAllBlocks:
    def __init__(self, as_block_value: AsBlockValue):
        self.as_block_value: AsBlockValue = as_block_value
        self.spec_to_block_tuple: DescriptorBlockToColumnBlocks = DescriptorBlockToColumnBlocks()

    def __call__(self, full_spec: List[Dict]) -> List[Block]:
        blocks: Deque[Block] = deque()
        for block_spec in full_spec:  # type: Dict
            assert len(block_spec) == 1
            block_type: str = list(block_spec.keys())[0]
            assert block_type in {"temporal_block", "immutable_block"}
            block_tuple: Tuple = self.spec_to_block_tuple(block_spec[block_type])
            build: Type = constructors[block_type]
            block: Block = build(block_tuple, self.as_block_value)
            blocks.append(block)
        return list(blocks)
