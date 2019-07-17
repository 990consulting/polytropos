from collections import deque
from dataclasses import field, dataclass
from typing import Deque, Iterator, NamedTuple, Optional, Any


class ValueMatch(NamedTuple):
    entity_id: str
    observation: str  # The period label, or "immutable" for immutable variables
    var_path: str
    data_type: str
    value: Optional[Any]

class ValueMismatch(NamedTuple):
    entity_id: str
    observation: str  # The period label, or "immutable" for immutable variables
    var_path: str
    data_type: str
    expected: Optional[Any]
    actual: Optional[Any]

class MissingValue(NamedTuple):
    entity_id: str
    observation: str  # The period label, or "immutable" for immutable variables
    var_path: str
    data_type: str
    expected: Optional[Any]

@dataclass
class Outcome:
    matches: Deque[ValueMatch] = field(init=False, default_factory=lambda: deque())
    mismatches: Deque[ValueMismatch] = field(init=False, default_factory=lambda: deque())
    missings: Deque[MissingValue] = field(init=False, default_factory=lambda: deque())

    @property
    def match_case_ids(self) -> Iterator[str]:
        pass

    @property
    def mismatch_case_ids(self) -> Iterator[str]:
        pass

    @property
    def missing_case_ids(self) -> Iterator[str]:
        pass
