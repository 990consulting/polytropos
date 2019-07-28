from typing import TextIO, Optional
import click

from polytropos.actions.consume.coverage import CoverageFile
from polytropos.ontology.task import Task
from polytropos.tools.schema import treeview
from polytropos.tools.schema.catalog import variable_catalog
from polytropos.tools.schema.linkage import ExportLinkages, ImportLinkages
from polytropos.tools.schema.repair_sort import repair_sort_order

@click.group()
def cli():
    """Polytropos. Copyright (c) 2019 Applied Nonprofit Research."""
    pass

@cli.command()
@click.argument('data_path', type=click.Path(exists=True))
@click.argument('config_path', type=click.Path(exists=True))
@click.argument('task_name', type=str)
def task(data_path: str, config_path: str, task_name: str):
    """Perform a Polytropos task."""
    task = Task.build(config_path, data_path, task_name)
    task.run()

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

@schema.command()
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
@click.argument('output_file', type=click.File('w'))
def catalog(schema_basepath: str, schema_name: str, output_file: TextIO):
    """Export a CSV-formatted catalog of variables in a schema."""
    variable_catalog(schema_basepath, schema_name, output_file)

@schema.command(name="treeview")
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
def schema_treeview(schema_basepath: str, schema_name: str):
    """Output an ASCII tree representation of a schema to stdout."""
    treeview.print_from_files(schema_basepath, schema_name)

@schema.command(name="repair")
@click.argument('schema_path', type=click.Path(exists=True))
def schema_repair(schema_path: str):
    """Replaces the existing sort order in a schema (if any) with an arbitrary, but valid, sort order. No aspect of the
    old sort order will be preserved; the new order will be alphabetized by variable name."""
    repair_sort_order(schema_path)

@cli.command()
@click.argument('schema_basepath', type=click.Path(exists=True))
@click.argument('schema_name', type=str)
@click.argument('data_path', type=click.Path(exists=True))
@click.argument('output_prefix', type=str)
@click.option('--t-group', type=str, default=None, help="Variable ID of temporal grouping variable, if any.")
@click.option('--i-group', type=str, default=None, help="Variable ID of immutable grouping variable, if any.")
def coverage(schema_basepath: str, schema_name: str, data_path: str, output_prefix: str, t_group: Optional[str],
             i_group: Optional[str]):
    """Produce a coverage report consisting of four files: coverage and groups for each of immutable and temporal
    tracks."""
    CoverageFile.standalone(schema_basepath, schema_name, data_path, output_prefix, t_group, i_group)
