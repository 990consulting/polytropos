from abc import abstractmethod
from collections.abc import Callable
from typing import Dict

from etl4.ontology.schema import Schema

class Change(Callable):
    """A transformation to be applied to a single composite. The transformation can create or alter any variable that
    is defined in the schema. As a matter of practice, however, the variables to be altered should be defined in the
    Mutation's parameters."""

    def __init__(self, schema: Schema, lookups: Dict, *subjects):
        """Except for the schema, all parameters to the constructor represent variable IDs."""
        # TODO All subjects should have a "subject" decorator. At construction time, all subjects should be validated
        #  according to their decorator and then replaced with a Variable object, by means of which its path,
        #  temporality, and other attributes may be accessed.
        # TODO All required lookups should have a "lookup" decorator. At construction time, the decorator will verify
        #  that the required lookup has been loaded.
        # TODO: In each of the Change implementations in the fixtures, I explicitly enumerate all the subjects both in
        #  the method parameters and in the decorators. I'll bet that you could use class decorators and __setattr__,
        #  and then none of the classes would even need to implement constructors.
        self.schema = schema
        self.lookups = lookups

    @classmethod
    def deserialize(cls, spec: Dict) -> "Change":
        # TODO Quimey,  you may wish to handle the Metamorphosis->Change serialization/deserialization process exactly
        #  as you did in the Track->Variable case, in which case please feel free to trash these stubs and rewrite any
        #  tests that depend on them.
        pass

    @abstractmethod
    def __call__(self, composite: Dict):
        """Perform the change on the supplied composite."""
        pass
