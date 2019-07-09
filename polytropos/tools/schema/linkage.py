import os
from collections.abc import Callable
from typing import Optional, List as ListType, TextIO, List, Iterable, Iterator

from polytropos.ontology.track import Track
from polytropos.util.nesteddicts import path_to_str, str_to_path
import csv

from polytropos.ontology.schema import Schema
from polytropos.ontology.variable import Variable

def _source_path(var: Variable, source_id: str) -> str:
    source_track: Track = var.track.source
    try:
        source_var: Variable = source_track[source_id]
    except Exception as e:
        print("breakpoint")
        raise e
    return path_to_str(source_var.absolute_path)

class ExportLinkages(Callable):
    """Export a .csv in which the first two columns are respectively the variable ID and the absolute path of the
    schema, and the subsequent columns are the absolute paths (not variable IDs!) of the sources."""

    def __init__(self, schema: Schema, fh: TextIO):
        self.schema: Schema = schema
        self.fh: TextIO = fh

    @classmethod
    def from_files(cls, schema_basepath: str, source_schema: str, target_schema: str, output_file: TextIO):
        source_schema_instance: Schema = Schema.load(source_schema, base_path=schema_basepath)
        target_schema_instance: Schema = Schema.load(target_schema, source_schema=source_schema_instance,
                                                     base_path=schema_basepath)
        export: "ExportLinkages" = cls(target_schema_instance, output_file)
        export()
        output_file.close()

    def __call__(self):
        writer = csv.writer(self.fh)
        for var in self.schema:  # type: Variable
            var_id: str = var.var_id
            abs_path: str = path_to_str(var.absolute_path)
            if not var.sources:
                writer.writerow([var_id, abs_path])
                continue
            row: ListType = [var_id, abs_path] + [_source_path(var, source_id) for source_id in var.sources]
            writer.writerow(row)

class ImportLinkages(Callable):
    """Import a .csv in the same format as that produced by export_linkages(), and modify the sources of the variables
    of the schema to reflect the ones in the file."""

    def __init__(self, schema: Schema, fh: TextIO):
        self.schema: Schema = schema
        self.fh: TextIO = fh

    @classmethod
    def from_files(cls, schema_basepath: str, source_schema: str, target_schema: str, input_file: TextIO, suffix: str):
        source_schema_instance: Schema = Schema.load(source_schema, base_path=schema_basepath)
        target_schema_instance: Schema = Schema.load(target_schema, source_schema=source_schema_instance,
                                                     base_path=schema_basepath)
        do_import: "ImportLinkages" = cls(target_schema_instance, input_file)
        do_import()
        input_file.close()
        output_schema_relpath: str = "%s_%s" % (target_schema, suffix)
        output_path: str = os.path.join(schema_basepath, output_schema_relpath)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        target_schema_instance.serialize(output_path)

    def _as_source_ids(self, source_paths: List[str]) -> Iterator[str]:
        for source_path_str in source_paths:
            path: Iterable[str] = str_to_path(source_path_str)
            var: Variable = self.schema.source.lookup(path)
            yield var.var_id

    def __call__(self):
        reader: csv.reader = csv.reader(self.fh)
        for line in reader:
            var_id, abs_path, *source_paths = line
            source_ids: Optional[List[str]] = list(self._as_source_ids(source_paths))
            if len(source_ids) == 0:
                source_ids = None

            # Make sure the user didn't try to modify the absolute path of the variable using this importer
            var_by_id: Variable = self.schema.get(var_id)
            var_by_path: Variable = self.schema.lookup(str_to_path(abs_path))
            if var_by_id is not var_by_path:
                raise SyntaxError("Cannot use linkage importer to modify absolute paths")
            var_by_id.sources = source_ids
