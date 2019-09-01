import itertools
from typing import List, Dict, Iterator, Optional, Any, Iterable, cast

from polytropos.actions.consume.tocsv.blocks.blockvalue import flatten
from polytropos.actions.consume.tocsv.blocks import Block, ImmutableBlock, TemporalBlock
from polytropos.ontology.composite import Composite

def _has_temporal(blocks: Iterable[Block]) -> bool:
    for block in blocks:
        if isinstance(block, TemporalBlock):
            return True
    return False

def init_or_multiply(block_value: Iterable, period: str, prior: Dict) -> None:
    if period not in prior:
        prior[period] = block_value
    else:
        prior[period] = list(itertools.product(prior[period], block_value))

class BlockProduct:
    """The final set of rows in a CSV for a given composite is actually the Cartesian product rows from a subgroup of
    the table's columns, called blocks. This method object produces the values for all such blocks and yields the full
    rows."""

    def __init__(self, composite: Composite, blocks: List[Block]):
        self.blocks = blocks
        self.composite: Composite = composite
        self.immutable_block_values: Dict[int, Iterator[List[Optional[Any]]]] = {}
        self.temporal_block_values: Dict[int, Dict[str, Iterator[List[Optional[Any]]]]] = {}
        self.has_temporal_subrows: bool = _has_temporal(blocks)

    # TODO: I think we can get rid of this and generate blocks on the fly
    def _resolve_block_values(self) -> None:
        for i, block in enumerate(self.blocks):
            if isinstance(block, ImmutableBlock):
                self.immutable_block_values[i] = block(self.composite)
            elif isinstance(block, TemporalBlock):
                self.temporal_block_values[i] = block(self.composite)
            else:
                raise ValueError

    def _with_periods(self) -> Iterator[List[Optional[Any]]]:
        """Takes Cartesian product of blocks only within the same period. Whenever an immutable block is encountered,
        the product is taken with preceding blocks from all periods. The first two columns are the composite ID and the
        period."""
        prior: Dict = {}
        periods: List[str] = sorted(self.composite.periods)

        # When a composite contains no temporal observations, temporal blocks contain a single key ("") representing a
        # block of nulls. See TemporalBlock in _blocks.py.
        if len(periods) == 0:
            periods = [""]

        for i, block in enumerate(self.blocks):
            if isinstance(block, ImmutableBlock):
                block_value: List = list(self.immutable_block_values[i])
                for period in periods:
                    init_or_multiply(block_value, period, prior)
            elif isinstance(block, TemporalBlock):
                period_block_values: Dict[str, Iterator] = self.temporal_block_values[i]
                for period in periods:
                    block_value = list(period_block_values[period])
                    init_or_multiply(block_value, period, prior)
            else:
                raise ValueError
        for period in periods:
            final: Iterable = list(itertools.product([[self.composite.composite_id, period]], prior[period]))
            for sub_row in final:
                debug: List = list(flatten(sub_row))
                yield debug

    def _without_periods(self) -> Iterator[List[Optional[Any]]]:
        """Takes simple Cartesian product of all blocks. First column is composite ID."""
        # noinspection PyTypeChecker
        prior: Optional[Iterator] = None
        for i in range(len(self.blocks)):
            assert i in self.immutable_block_values, "All blocks are purportedly immutable, but block %i is missing" % i
            if prior is None:
                prior = self.immutable_block_values[i]
            else:
                prior = itertools.product(prior, self.immutable_block_values[i])
        prior = cast(Iterator, prior)
        final: Iterator = itertools.product([self.composite.composite_id], prior)
        for sub_row in final:
            yield list(flatten(sub_row))

    def __call__(self) -> Iterator[List[Optional[Any]]]:
        self._resolve_block_values()
        if self.has_temporal_subrows:
            yield from self._with_periods()
        else:
            yield from self._without_periods()
