from typing import Tuple, Dict, Iterator, List, Optional, Any

from attr import dataclass

from polytropos.actions.consume.tocsv.blocks.blockvalue import AsBlockValue
from polytropos.actions.consume.tocsv.topo import Topological

from polytropos.ontology.composite import Composite

@dataclass(cmp=False)  # type: ignore # cmp is deprecated, use eq and order
class Block:
    contents: Tuple
    as_block_value: AsBlockValue

    def _for_period(self, composite: Composite, period: str) -> Iterator[List[Optional[Any]]]:
        topo: Topological = Topological(composite, period)
        values: Dict = topo(self.contents)
        yield from self.as_block_value(self.contents, values)

    def __eq__(self, other: Any) -> bool:
        if other.__class__ != self.__class__:
            return False
        if other.contents != self.contents:
            return False
        return True

class ImmutableBlock(Block):
    def __call__(self, composite: Composite) -> Iterator[List[Optional[Any]]]:
        yield from self._for_period(composite, "immutable")

class TemporalBlock(Block):
    def __call__(self, composite: Composite) -> Dict[str, Iterator[List[Optional[Any]]]]:
        ret: Dict[str, Iterator[List[Optional[Any]]]] = {}
        for period in composite.periods:
            ret[period] = self._for_period(composite, period)

        if len(ret) == 0:
            ret[""] = self.as_block_value(self.contents, {})
        return ret
