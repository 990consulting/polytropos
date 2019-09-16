from typing import TextIO, Dict, Optional
import csv

from polytropos.util.nesteddicts import path_to_str

from polytropos.ontology.schema import Schema
from polytropos.ontology.track import Track

def _process_track(track: Track, temporality: str, writer: csv.DictWriter) -> None:
    rows: Dict[str, Dict[str, str]] = {}
    for var_id, variable in track.items():
        abs_path: str = path_to_str(variable.absolute_path)
        row: Dict = {
            "variable_id": var_id,
            "absolute_path": abs_path,
            "data_type": variable.data_type,
            "temporality": temporality
        }
        rows[abs_path] = row

    for abs_path in sorted(rows.keys()):
        row = rows[abs_path]
        writer.writerow(row)

def write_catalog(schema: Schema, fh: TextIO) -> None:
    """Produce a spreadsheet containing variable ID, absolute path, data type, and temporality."""
    writer: csv.DictWriter = csv.DictWriter(fh, ["variable_id", "absolute_path", "data_type", "temporality"])
    writer.writeheader()
    _process_track(schema.temporal, "temporal", writer)
    _process_track(schema.immutable, "immutable", writer)

def variable_catalog(schema_basepath: str, schema_name: str, fh: TextIO) -> None:
    schema: Optional[Schema] = Schema.load(schema_name, schema_basepath)
    assert schema is not None
    write_catalog(schema, fh)
    fh.close()