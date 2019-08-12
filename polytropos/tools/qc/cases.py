from typing import NamedTuple, Optional, Any, Iterator, Tuple
from attr import dataclass

from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import VariableId


class TestCase(NamedTuple):
    immutable: bool
    period: Optional[str]
    var_id: VariableId
    expected_value: Optional[Any]

@dataclass
class FindCasesForFixture:
    """Finds every test case within a given fixture."""

    schema: Schema
    fixture: Composite

    def _find_cases_for_period(self) -> Iterator[TestCase]:
        pass

    def _find_temporal_cases(self) -> Iterator[TestCase]:
        pass

    def _find_immutable_cases(self) -> Iterator[TestCase]:
        pass

    def __call__(self) -> Iterator[TestCase]:
        yield from self._find_temporal_cases()
        yield from self._find_immutable_cases()

@dataclass
class FindTestCases:
    """Finds every test case in every composite within a data directory."""

    schema: Schema     # The schema in which the fixtures are encoded
    fixture_path: str  # The path in which to find the fixtures

    def _fixtures(self) -> Iterator[Tuple[str, Composite]]:
        # TODO Implement me
        pass

    def _for_fixture(self, fixture: Composite) -> Iterator[TestCase]:
        find_cases: FindCasesForFixture = FindCasesForFixture(self.schema, fixture)
        yield from find_cases()

    def __call__(self) -> Iterator[Tuple[str, Iterator[TestCase]]]:
        for fixture_id, fixture in self._fixtures():
            yield fixture_id, self._for_fixture(fixture)
