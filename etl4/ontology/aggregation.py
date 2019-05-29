from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator

# TODO Quimey, if it doesn't make it too difficult to implement with parallelism, supporting lookups here would be
#  great.
class Aggregation(ABC):
    """Iterates over all composites following one schema, and produces a new set of composites, representing a different
    kind of entity, and following a different schema."""

    @classmethod
    def build(
            cls, path_locator, schema, name, target_schema, id_var,
            input_schema_vars, output_schema_vars
    ): 
        pass

    @abstractmethod
    def extract(self, composite: Dict) -> Optional[Any]:
        """Gather the information to be used in the analysis."""
        pass

    @abstractmethod
    def analyze(self, extracts: Iterable[Tuple[str, Any]]) -> None:
        """Collect, process, and store the global information provided from each composite during the scan() step.
        :param extracts: Tuple of (composite id, whatever is returned by extract)"""
        pass

    @abstractmethod
    def emit(self) -> Iterator[Tuple[str, Dict]]:
        """Lazily produce instances of the target entity. Yields tuples of (new entity ID, new entity content)."""
        pass
