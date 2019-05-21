from typing import Dict, List

class Metamorphosis:
    """A metamorphosis represents a series of changes that are made to a single composite, in order, and without
    reference to any other composite. Each change is defined in terms of one or more subject variables, which may be
    inputs, outputs, or both (in a case where a change alters a value in place)."""

    def __init__(self, changes: List):
        self.changes = changes

    @classmethod
    def deserialize(cls, specs: Dict) -> "Metamorphosis":
        """Loads in the specified lookup tables, constructs the specified Changes, and passes these Changes to the
        constructor."""
        pass

    def __call__(self, composite: Dict) -> None:
        for change in self.changes:
            change(composite)
