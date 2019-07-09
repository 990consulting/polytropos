from typing import TextIO

from polytropos.tools.schema.linkage import ExportLinkages
from polytropos.ontology.schema import Schema

schema_basepath: str = "/dmz/github/analysis/etl5/schemas"
schema_relpath: str = "nonprofit/logical"
output_file: TextIO = open("/tmp/logical_linkages.csv", "w")

schema: Schema = Schema.load(schema_relpath, base_path=schema_basepath)
export: ExportLinkages = ExportLinkages(schema, output_file)
export()
output_file.close()
