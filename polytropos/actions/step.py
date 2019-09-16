from abc import abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from polytropos.ontology.context import Context
    from polytropos.ontology.schema import Schema

class Step:

    @classmethod
    @abstractmethod
    def build(cls, *, context: "Context", schema: "Schema", **kwargs: Any) -> Any:
        """Build takes always a context and a schema, there are other
        keyword arguments that depend on the implementation"""
        pass

    @abstractmethod
    def __call__(self, origin_dir: str, target_dir: str) -> None:
        """Call takes the origin folder and the target folder"""
        pass
