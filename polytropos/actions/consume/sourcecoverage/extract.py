import json
import logging
import os
import uuid
from typing import Dict, List

from polytropos.actions.consume.sourcecoverage.result import SourceCoverageResult

from polytropos.actions.consume.sourcecoverage.crawl import Crawl
from polytropos.ontology.composite import Composite
from polytropos.ontology.schema import Schema
from polytropos.util.paths import relpath_for

class SourceCoverageExtract:
    """Produces source coverage result for a chunk of composites.
    Can be called on separate process (all instance fields ard arguments/results of methods are serializable).
    """

    def __init__(self, schema: Schema, translate_dir: str, trace_dir: str, temp_dir: str):
        self.schema = schema
        self.translate_dir = translate_dir
        self.trace_dir = trace_dir
        self.temp_dir = temp_dir

    def _extract(self, translate_composite: Composite, trace_composite: Composite, result: SourceCoverageResult) -> None:
        composite_id = translate_composite.composite_id
        crawl: Crawl = Crawl(composite_id, self.schema)
        translation: Dict = translate_composite.content
        trace: Dict = trace_composite.content
        composite_result: SourceCoverageResult = crawl(translation, trace)
        result.update(composite_result)

    def _load_composite(self, base_dir: str, composite_id: str) -> Composite:
        relpath: str = relpath_for(composite_id)
        composite_path = os.path.join(base_dir, relpath, "%s.json" % composite_id)
        content: Dict
        if not os.path.exists(composite_path):
            content = {}
        else:
            with open(os.path.join(base_dir, relpath, "%s.json" % composite_id)) as translate_file:
                content = json.load(translate_file)
        return Composite(self.schema, content, composite_id=composite_id)

    def extract(self, composite_ids: List[str]) -> str:
        """Produces source coverage result for a chunk of composites."""

        result = SourceCoverageResult()
        for composite_id in composite_ids:
            logging.debug("Extracting data from composite %s", composite_id)

            translate_composite: Composite = self._load_composite(self.translate_dir, composite_id)
            trace_composite: Composite = self._load_composite(self.trace_dir, composite_id)
            self._extract(translate_composite, trace_composite, result)

        state_path = os.path.join(self.temp_dir, str(uuid.uuid4()))
        result.serialize_state(state_path)
        return state_path
