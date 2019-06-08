from dataclasses import dataclass
from typing import Dict

from polytropos.actions.consume import Consume

# TODO: Quimey, Since this file might be huge, this needs to be done in a streaming fashion, so I recommend opening a
#  filehandle for writing and writing an opening curly brace in the "before" step, and a closing curly brace in the
#  "after" step. In each consume step, emit '"<composite_id>": <composite>. On all but the first one, you will also
#  need to emit ', ' at the start of each composite.

@dataclass
class ExportToJSON(Consume):
    filename: str

    """Create a single JSON file consisting of a JSON dict, where the keys are the composite IDs and the values are the
    composites themselves. """
    def before(self):
        pass

    def consume(self, composite_id: str, composite: Dict):
        pass

    def after(self):
        pass