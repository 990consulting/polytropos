from abc import abstractmethod
from collections.abc import Callable


class Step(Callable):
    """ABC for all tasks steps"""
    @classmethod
    @abstractmethod
    def build(cls, path_locator, schema, **kwargs):
        """Build takes always a path locator and a schema, there are other
        keyword arguments that depend on the implementation"""
        pass

    @abstractmethod
    def __call__(self, origin, target):
        """Call takes the origin folder and the target folder"""
        pass
