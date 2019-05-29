from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

@dataclass
class Filter(ABC):
    """Iterates over each composite, removing some of them if they do not meet some criterion."""

    @abstractmethod
    def passes(self, composite: Dict) -> bool:
        pass