from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from polytropos.ontology.paths import PathLocator
    from polytropos.ontology.schema import Schema

class Step(Callable):

    @classmethod
    @abstractmethod
    def build(cls, *, path_locator: "PathLocator", schema: "Schema", **kwargs):
        """Build takes always a path locator and a schema, there are other
        keyword arguments that depend on the implementation"""
        pass

    @abstractmethod
    def __call__(self, origin_dir: str, target_dir: str):
        """Call takes the origin folder and the target folder"""
        pass
