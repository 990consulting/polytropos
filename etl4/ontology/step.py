from abc import abstractmethod
from collections.abc import Callable


class Step(Callable):
    """ABC for all tasks steps"""
    @classmethod
    @abstractmethod
    def build(cls, path_locator, schema, **kwargs):
        pass

    @abstractmethod
    def __call__(self, origin, target):
        pass
