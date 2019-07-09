from typing import TextIO
import click

from polytropos.tools.schema.linkage import ExportLinkages, ImportLinkages

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
    ExportLinkages.from_files(schema_basepath, source_schema, target_schema, output_file)

@linkage.command(name="import")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('source_schema', type=str)
@click.argument('target_schema', type=str)
@click.argument('input_file', type=click.File('r'))
@click.option('-s', '--suffix', default="_revised", type=str)
def linkage_import(schema_basepath: str, source_schema: str, target_schema: str, input_file: TextIO, suffix: str):
    """Import a modified translation linkage and output it."""
    ImportLinkages.from_files(schema_basepath, source_schema, target_schema, input_file, suffix)