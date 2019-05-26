from abc import ABC, abstractmethod
from typing import Dict

class Filter(ABC):
    """Iterates over each composite, removing some of them if they do not meet some criterion."""

    @abstractmethod
    def passes(self, composite: Dict) -> bool:
        pass