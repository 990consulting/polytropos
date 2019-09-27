from dataclasses import dataclass
from abc import abstractmethod
from typing import Dict

from polytropos.ontology.composite import Composite

from polytropos.ontology.schema import Schema


@dataclass # type: ignore # https://github.com/python/mypy/issues/5374
class Change:
    """A transformation to be applied to a single composite. The transformation can create or alter any variable that
    is defined in the schema. As a matter of practice, however, the variables to be altered should be defined in the
    Mutation's parameters."""
    schema: Schema
    lookups: Dict

    @abstractmethod
    def __call__(self, composite: Composite) -> None:
        """Perform the change on the supplied composite."""
        pass
