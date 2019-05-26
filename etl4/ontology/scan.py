from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Iterable, Tuple

class Scan(ABC):
    """Scan iterates through all of the composites in the task pipeline twice: once to gather global information, and
    then a second time to make alterations to the composites on the basis of the globally gathered information. In
    between, an arbitrary analysis may be performed on the basis of the global information. Example use cases include
    assigning ranks, or computing a property relative to peers sharing some other property."""

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
    def alter(self, composite_id: str, composite: Dict) -> None:
        """Alter the supplied composite in place. The resulting composite will then overwrite the original, completing
        the alteration."""
        pass