from dataclasses import dataclass
from typing import Dict, Iterator, Optional, Any

from polytropos.ontology.schema import Schema

@dataclass
class Composite:
    schema: Schema
    content: Dict
