import csv
import logging
import os
from dataclasses import dataclass, field
from typing import Iterable, Any, Optional, List

from polytropos.actions.consume import Consume
from polytropos.actions.consume.source_coverage._source_coverage_extract import SourceCoverageExtract
from polytropos.actions.consume.source_coverage._source_coverage_result import SourceCoverageResult
from polytropos.ontology.composite import Composite
from polytropos.ontology.context import Context
from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable
from polytropos.util import nesteddicts
from polytropos.util.paths import find_all_composites


@dataclass  # type: ignore # https://github.com/python/mypy/issues/5374
class SourceCoverage(Consume):
    """Generates source coverage report (a csv file)."""

    translate_dir: str
    trace_dir: str
    output_filename: Optional[str] = None

    coverage_result: SourceCoverageResult = field(default_factory=SourceCoverageResult, init=False)

    # noinspection PyTypeChecker
    @classmethod
    def standalone(cls, context: Context, translate_dir: str, trace_dir: str, source_schema_name: str, target_schema_name: str, output_filename: str) -> None:
        source_schema: Optional[Schema] = Schema.load(source_schema_name, context.schemas_dir)
        assert source_schema is not None

        schema: Optional[Schema] = Schema.load(target_schema_name, context.schemas_dir, source_schema)
        assert schema is not None

        coverage: "SourceCoverage" = cls(context, schema, translate_dir, trace_dir, output_filename)
        coverage("dummy", None)

    def before(self) -> None:
        pass

    def extract(self, composite: Composite) -> SourceCoverageResult:
        raise NotImplementedError

    def consume(self, extracts: Iterable[Any]) -> None:
        for extract in extracts:
            self.coverage_result.merge_serialized_state(extract)

    def _write_coverage_file(self) -> None:
        output_filename: str = self.output_filename or "source_coverage.csv"
        fn: str = os.path.join(self.context.output_dir, output_filename)
        logging.info("Writing coverage file to %s.", fn)

        columns: List[str] = ["source_var_id", "source_var_path", "target_var_id", "target_var_path", "data_type", "n"]

        source_schema = self.schema.source
        assert source_schema is not None

        with open(fn, "w") as fh:
            writer: csv.DictWriter = csv.DictWriter(fh, columns)
            writer.writeheader()
            for var_info in sorted(self.coverage_result.all_vars):
                source_var_id = var_info.source_var_id
                target_var_id = var_info.target_var_id

                logging.debug("Writing coverage for %s -> %s.", source_var_id, target_var_id)
                source_var: Optional[Variable] = source_schema.get(source_var_id)
                target_var: Optional[Variable] = self.schema.get(target_var_id)
                assert source_var is not None and target_var is not None

                row = {
                    "source_var_id": source_var_id,
                    "source_var_path": nesteddicts.path_to_str(source_var.absolute_path),
                    "target_var_id": target_var_id,
                    "target_var_path": nesteddicts.path_to_str(target_var.absolute_path),
                    "data_type": source_var.data_type,
                    "n": self.coverage_result.var_counts.get(var_info, 0)
                }
                writer.writerow(row)

    def after(self) -> None:
        self._write_coverage_file()

    def process_composites(self, composite_ids: Iterable[str], origin_dir: str) -> Iterable[Any]:
        raise NotImplementedError

    def __call__(self, _origin_dir: str, _target_dir: Optional[str]) -> None:
        self.before()

        translate_composite_ids = set(find_all_composites(self.translate_dir))
        trace_composite_ids = set(find_all_composites(self.trace_dir))
        assert translate_composite_ids.issubset(trace_composite_ids)

        coverage = SourceCoverageExtract(self.schema, self.translate_dir, self.trace_dir, self.context.temp_dir)
        per_composite_results: List[str] = list(self.context.run_in_process_pool(coverage.extract, list(trace_composite_ids)))
        logging.info("Merging chunk results.")
        self.consume(per_composite_results)
        self.after()
