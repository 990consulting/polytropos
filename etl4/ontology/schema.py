from etl4.ontology.track import Track
from dataclasses import dataclass

@dataclass
class Schema:
    """A schema identifies all of the temporal and invariant properties that a particular entity can have."""
    temporal: Track
    invariant: Track
