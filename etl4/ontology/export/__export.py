from collections.abc import Callable
from abc import abstractmethod
from typing import Tuple, Dict, Iterable

class Export(Callable):
    """Export data from a set of composites to a single file."""

    @abstractmethod
    def __call__(self, composites: Iterable[Tuple[str, Dict]]):
        """Generate the export file."""
        pass