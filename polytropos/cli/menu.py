import os
from typing import TextIO
import click

from polytropos.cli.linkage import ExportLinkages, ImportLinkages
from polytropos.ontology.schema import Schema

@click.group()
def cli():
    """Polytropos. Copyright (c) 2019 Applied Nonprofit Research."""
    pass

@cli.group()
def schema():
    """Commands for viewing and manipulating schemas."""
    pass

@schema.group()
def linkage():
    """Import and export translation linkages."""
    pass

@linkage.command(name="export")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('output_file', type=click.File('w'))
def linkage_export(schema_basepath: str, source_schema: str, target_schema: str, output_file: TextIO):
    """Export a translation linkage."""
    source_schema_instance: Schema = Schema.load(source_schema, base_path=schema_basepath)
    target_schema_instance: Schema = Schema.load(target_schema, source_schema=source_schema_instance,
                                                 base_path=schema_basepath)
    export: ExportLinkages = ExportLinkages(target_schema_instance, output_file)
    export()
    output_file.close()

@linkage.command(name="import")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('input_file', type=click.File('r'))
@click.option('-s', '--suffix', default="_revised", type=str)
def linkage_import(schema_basepath: str, source_schema: str, target_schema: str, input_file: TextIO, suffix: str):
    """Import a modified translation linkage and output it."""
    source_schema_instance: Schema = Schema.load(source_schema, base_path=schema_basepath)
    target_schema_instance: Schema = Schema.load(target_schema, source_schema=source_schema_instance,
                                                 base_path=schema_basepath)
    do_import: ImportLinkages = ImportLinkages(target_schema_instance, input_file)
    do_import()
    input_file.close()
    output_schema_relpath: str = "%s_%s" % (target_schema, suffix)
    output_path: str = os.path.join(schema_basepath, output_schema_relpath)
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    target_schema_instance.serialize(output_path)