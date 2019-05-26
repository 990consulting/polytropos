from abc import ABC, abstractmethod

class Aggregation(ABC):
    """Iterates over all composites following one schema, and produces a new set of composites, representing a different
    kind of entity, and following a different schema."""