from abc import abstractmethod
from collections.abc import Callable
from typing import Dict, Optional, Any, Iterable, Tuple, Iterator

# TODO Quimey, there's TONS of examples of this out there, and I bet there's a nice library for it.
class Diff(Callable):
    """Compares composites with the same ID and from the same schema, identifying differences."""

    def __call__(self, expected: Dict, actual: Dict) -> Dict:
        """Compare the two Dicts and emit a third Dict of differences."""
        pass