from dataclasses import dataclass
from typing import Dict, Any

from polytropos.actions.translate import Translate
from polytropos.actions.translate.__document import DocumentValueProvider
from polytropos.actions.translate.trace.__trace_document import TraceDocumentValueProvider


@dataclass
class Trace(Translate):
    @staticmethod
    def create_document_value_provider(doc: Dict[str, Any]) -> DocumentValueProvider:
        return TraceDocumentValueProvider(doc)
