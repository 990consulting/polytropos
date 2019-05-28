from collections.abc import Callable
from abc import abstractmethod
from typing import Tuple, Dict, Iterable

class Consume(Callable):
    """Consume all of the composites, typically for the purpose of creating an export."""

    @abstractmethod
    def __call__(self, composites: Iterable[Tuple[str, Dict]]):
        """Generate the export file."""
        pass