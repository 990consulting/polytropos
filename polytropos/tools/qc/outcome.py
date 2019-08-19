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
        for match in self.matches:
            yield "/%s/%s%s" % (match.entity_id, match.observation, match.var_path)

    @property
    def mismatch_case_ids(self) -> Iterator[str]:
        for mismatch in self.mismatches:
            yield "/%s/%s%s" % (mismatch.entity_id, mismatch.observation, mismatch.var_path)

    @property
    def missing_case_ids(self) -> Iterator[str]:
        for missing in self.missings:
            yield "/%s/%s%s" % (missing.entity_id, missing.observation, missing.var_path)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        if set(other.matches) != set(self.matches):
            return False

        if set(other.mismatches) != set(self.mismatches):
            return False

        if set(other.missings) != set(self.missings):
            return False

        return True